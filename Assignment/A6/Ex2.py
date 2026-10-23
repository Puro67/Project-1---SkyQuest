import random
sides = int(input("How many sides? "))
def roll_dice(sides):
    return random.randint(1, sides)
roll = roll_dice(sides)

while roll != sides:
    print(roll)
    roll = roll_dice(sides)
print(roll)