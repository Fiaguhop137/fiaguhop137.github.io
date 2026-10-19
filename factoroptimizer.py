import math
def factors(number:int)->list[int]:
    result=[]
    for i in range(1,math.isqrt(number)+1):
        if number%i==0:
            result.append(i)
            if i!=number//i:
                result.append(number//i)
    return result
active_number=0
highest_number_factor_count=0
while True:
    active_number+=1
    current_number_factor_count=len(factors(active_number))
    if current_number_factor_count>=highest_number_factor_count:
        highest_number_factor_count=current_number_factor_count
        highest_number=active_number
        stagnation=0
        print(f"New highest factor count found: {highest_number_factor_count} for number {active_number}. ")