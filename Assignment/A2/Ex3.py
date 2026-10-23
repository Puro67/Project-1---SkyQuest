length = int(input("enter the length of the circle: "))
height = int(input("enter the height of the circle: "))
if length > height:
    print ("the length of the circle is greater than the heigh, please enter another one")
    length = int(input("enter the length of the circle: "))
    height = int(input("enter the height of the circle: "))
print ("the area of the circle is", length * height)
print ("the perimeter of the circle is", (length + height) * 2)