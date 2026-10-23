import math

def calculate_unit_price(diameter_cm, price_euros):
    radius_m = (diameter_cm / 100) / 2
    area_m2 = math.pi * (radius_m ** 2)
    unit_price = price_euros / area_m2
    return unit_price


print("--- Pizza Value Comparison ---")

d1 = float(input("Enter diameter of the first pizza (cm): "))
p1 = float(input("Enter price of the first pizza (euros): "))

d2 = float(input("Enter diameter of the second pizza (cm): "))
p2 = float(input("Enter price of the second pizza (euros): "))

unit_price_1 = calculate_unit_price(d1, p1)
unit_price_2 = calculate_unit_price(d2, p2)

print(f"\nPizza 1 unit price: {unit_price_1:.2f} euros/square meters")
print(f"Pizza 2 unit price: {unit_price_2:.2f} euros/square meters")

if unit_price_1 < unit_price_2:
    print("Pizza 1 provides better value for money!")
elif unit_price_2 < unit_price_1:
    print("Pizza 2 provides better value for money!")
else:
    print("Both pizzas offer the exact same value for money.")