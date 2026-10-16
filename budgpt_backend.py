import json,queue,threading,time,ollama,requests
from datetime import datetime
DB_BASE_URL="https://discord-fia-default-rtdb.firebaseio.com"
NODE_PATH="/budgpt"
MODEL="dolphin-mistral"
message_queue=queue.Queue()
queued_ids=set()
queued_ids_lock=threading.Lock()
def log(message):
    timestamp=datetime.now().astimezone().isoformat(timespec="milliseconds")
    print(f"[{timestamp}] {message}",flush=True)
def post_message(content):
    url=f"{DB_BASE_URL}{NODE_PATH}.json"
    response=requests.post(url,json={"from": "server", "content": content},timeout=30)
    response.raise_for_status()
    result=response.json()
    msg_id=result.get("name")
    if not msg_id:
        raise RuntimeError(f"Firebase did not return a message ID: {result!r}")
    return msg_id
def delete_message(msg_id):
    url=f"{DB_BASE_URL}{NODE_PATH}/{msg_id}.json"
    response=requests.delete(url,timeout=30)
    response.raise_for_status()
def enqueue_message(msg_id, data):
    if not isinstance(data, dict):return
    if data.get("from")!="client":return
    content=data.get("content")
    if not isinstance(content, str) or not content.strip():
        log(f"Ignoring empty client message {msg_id}")
        return
    with queued_ids_lock:
        if msg_id in queued_ids:
            log(f"Already queued; ignoring duplicate event for {msg_id}")
            return
        queued_ids.add(msg_id)
    message_queue.put((msg_id, content))
    log(f"QUEUED {msg_id}: {content!r}")
def handle_event(event_data):
    if not isinstance(event_data, dict):
        log(f"Ignoring non-object event data: {event_data!r}")
        return
    path=event_data.get("path")
    data=event_data.get("data")
    log(f"Firebase update: path={path!r}, data_type={type(data).__name__}")
    if path=="/"and isinstance(data,dict):
        for msg_id,message_data in data.items():enqueue_message(msg_id, message_data)
    elif isinstance(path,str) and path!="/" and isinstance(data, dict):
        msg_id=path.strip("/")
        if msg_id:enqueue_message(msg_id, data)
    elif isinstance(path,str) and path!="/" and data is None:log(f"Firebase reports deletion at {path}")
    else:log(f"Unhandled Firebase update: {event_data!r}")
def process_message(msg_id,content):
    log(f"PROCESSING {msg_id}: {content!r}")
    for attempt in range(1,4):
        try:
            result=ollama.chat(model=MODEL,messages=[{"role":"user","content":content}])
            reply=result["message"]["content"]
            reply_id=post_message(reply)
            log(f"POSTED REPLY {reply_id} FOR {msg_id}")
            delete_message(msg_id)
            log(f"DELETED CLIENT MESSAGE {msg_id}")
            return True
        except Exception as error:
            log(f"Attempt {attempt}/3 failed for {msg_id}: {type(error).__name__}: {error}")
            if attempt<3:
                time.sleep(attempt*2)
    log(f"FAILED after 3 attempts: {msg_id}; client message retained")
    return False
def worker():
    while True:
        msg_id,content=message_queue.get()
        try:
            success=process_message(msg_id, content)
            if not success:
                with queued_ids_lock:
                    queued_ids.discard(msg_id)
        except Exception as error:log(f"Worker error: {type(error).__name__}: {error}")
        finally:message_queue.task_done()
def read_sse_stream(response):
    event_name="message"
    data_lines=[]
    while True:
        line=response.raw.readline()
        if not line:
            log("SSE stream returned EOF")
            return
        line=line.decode("utf-8", errors="replace").rstrip("\r\n")
        if line=="":
            if data_lines:
                payload="\n".join(data_lines)
                log(f"SSE EVENT RECEIVED: {event_name}; data={payload}")
                if event_name in ("put", "patch"):
                    try:
                        handle_event(json.loads(payload))
                    except json.JSONDecodeError as error:
                        log(f"Invalid JSON in SSE event: {error}")
            event_name="message"
            data_lines=[]
            continue
        if line.startswith(":"):
            log(f"SSE KEEP-ALIVE: {line[1:].strip()}")
            continue
        field,separator,value=line.partition(":")
        if separator and value.startswith(" "):value=value[1:]
        if field=="event":event_name=value
        elif field=="data":data_lines.append(value)
def start_realtime_stream():
    stream_url=f"{DB_BASE_URL}{NODE_PATH}.json"
    threading.Thread(target=worker,daemon=True,name="budgpt-worker").start()
    while True:
        try:
            log(f"Connecting to Firebase: {stream_url}")
            with requests.get(stream_url,stream=True,headers={"Accept":"text/event-stream","Cache-Control":"no-cache"},timeout=(15, None),) as response:
                response.raise_for_status()
                log(f"Firebase connected: HTTP {response.status_code}")
                log(f"Content-Type: {response.headers.get('Content-Type')!r}")
                response.raw.decode_content=False
                response.raw._fp.fp.raw._sock.settimeout(60)
                read_sse_stream(response)
        except KeyboardInterrupt:
            log("Stopped by keyboard interrupt")
            break
        except Exception as error:log(f"Firebase stream error: {type(error).__name__}: {error}")
        log("Reconnecting to Firebase in 3 seconds")
        time.sleep(3)
start_realtime_stream()
