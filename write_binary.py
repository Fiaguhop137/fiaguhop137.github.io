import os
if input()=="write":
    sin=input()
    if any(c not in "01" for c in sin):
        print("You ABSOLUTE IDIOT! Binary can only be 0s and 1s.")
        exit()
    if len(sin)%8!=0:
        sin+="0"*(8-(len(sin)%8))
    with open("out.bin","wb") as f:
        for i in range(0,len(sin),8):
            f.write(bytes([int(sin[i:i+8],2)]))
else:
    try:
        with open("out.bin","rb") as f:
            byte_data=f.read()
            for byte in byte_data:
                print(bin(byte)[2:].zfill(8),end="")
                with open("tmp.bin","a") as a:
                    a.write(bin(byte)[2:].zfill(8))
        with open("tmp.bin","r") as a:
            with open("out.bin","w") as f:
                f.write(a.read())
        os.remove("tmp.bin")
    except FileNotFoundError:
        print("You ABSOLUTE IDIOT and you didn't make a binary file yet. Run the program in write mode first.")