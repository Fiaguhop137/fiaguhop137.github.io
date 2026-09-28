def collatz_next(n):
    if n%2==0:
        return n//2
    else:
        return 3*n+1
cache={}
with open("collatz.json","w") as collatz:
    collatz.write("{\n    \"0\": [0]\n}")
i=0
while True:
    i+=1
    old=[i]
    while True:
        now=old[-1]
        if now in cache:
            new=cache[now]
        else:
            new=collatz_next(now)
            cache[now]=new
        if new in old:
            break
        old.append(new)
        print(f"{now} -> {new}")
    with open("collatz.json","r+b") as file:
        file.seek(0,2)
        file.seek(file.tell()-2)
        file.truncate()
        file.write(f',\n    "{i}": {old}\n}}'.encode('utf-8'))