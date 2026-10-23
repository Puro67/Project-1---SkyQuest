gasoline = int(input("volume in gallons:"))

while gasoline >= 0:
    litres = 3.78541 * gasoline
    print(f"volume in litres:{litres}")
    gasoline = int(input("volume in gallons:"))
print("Invalid number")