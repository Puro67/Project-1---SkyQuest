import random

def roll_dice():
    return random.randint(1, 6)
roll = roll_dice()

while roll != 6:
    print(roll)
    roll = roll_dice()
print(roll)