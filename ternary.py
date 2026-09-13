pot=[243,81,27,9,3,1]
ende=input("Encode or Decode? ")
code=input(f"What would you like to {ende}? ")
def encode(code):
    btarr=["======"]*len(code)
    for j in range(len(code)):
        b10=ord(code[j])-364  
        out=["=","=","=","=","=","="]
        for i in range(len(pot)):
            tspos=abs(b10-pot[i])
            tsneg=abs(b10+pot[i])
            smallest=min(tspos,tsneg,abs(b10))
            if (smallest==tspos):
                out[i]="+"
                b10-=pot[i]
            elif smallest==tsneg:
                out[i]="-"
                b10+=pot[i]
        btarr[j]="".join(out)
    return("".join(btarr))
def decode(code):
    b10arr=[0]*len(code)//6
    for i in range(len(code)//6):
        bt=code[i*6:i*6+6]
        for j in range(6):
            if bt[j]=="+":
                b10arr[i]+=pot[j]
            elif bt[j]=="-":
                b10arr[i]-=pot[j]
        b10arr[i]=chr(b10arr[i]+364)
    return("".join(b10arr))
if ende=="encode":
    print(encode(code))
elif ende=="decode":
    print(decode(code))
else:
    print("Invalid input, please enter encode or decode")