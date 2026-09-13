import random
print("".join(random.choice("0123456789abcdef") for _ in range(int(input("Enter the length of the random hex code: ")))))