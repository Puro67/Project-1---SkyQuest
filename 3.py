num1 =int(input("Please input the number:"))
num2 =1
while(num1 < 0):
    print("Program end")
    if (num1 > 0):
        num2 *= num1
        num1 -= 1
        print(num2)
