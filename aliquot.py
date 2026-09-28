def aliquot_sum(n):
    if n<=1:
        return 0
    total=1
    i=2
    while i*i<=n:
        if n%i==0:
            total+=i
            if i!=n//i:
                total+=n//i
        i+=1
    return total
cache={}
with open("aliquot.json","w") as aliquot:
    aliquot.write("{\n    \"0\": [0]\n}")
i=0
while True:
    i+=1
    old=[i]
    while True:
        now=old[-1]
        if now in cache:
            new=cache[now]
        else:
            new=aliquot_sum(now)
            cache[now]=new
        if new in old:
            break
        old.append(new)
        print(f"{now} -> {new}")
    with open("aliquot.json","r+b") as file:
        file.seek(0,2)
        file.seek(file.tell()-2)
        file.truncate()
        file.write(f',\n    "{i}": {old}\n}}'.encode('utf-8'))