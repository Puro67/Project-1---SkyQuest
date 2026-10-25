import random
num1 = random.randint(1,100)

num2 = int(input("Guest the number:"))
while (num1 != num2):
    if (num1 > num2):
        print("Too low")
    else:
        print("Too high")
    num2 = int(input("Guest again number:"))
print("Correct!")