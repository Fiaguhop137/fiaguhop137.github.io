import random
from time import perf_counter
def add(a,b):
    while not a==0:
        c=random.choice([-1,1])
        a+=c
        b-=c
    return b
t=perf_counter()
print(f"The answer is {add(int(input("What is your first number? ")),int(input("What is your second number? ")))}")
print(f"It took {round((perf_counter()-t)*1000)/1000} seconds to find this answer! ")