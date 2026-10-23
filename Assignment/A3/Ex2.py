cabin_class = str(input("enter the cabin class of the cruise ship: "))
if cabin_class == 'LUX':
    print ("It is an upper-deck cabin with a balcony.")
elif cabin_class == 'A':
    print ("It is above the car deck, equipped with a window")
elif cabin_class == 'B':
    print ("It is windowless cabin above the car deck.")
elif cabin_class == 'C':
    print ("It is windowless cabin below the car deck.")
else:
    print ("Invalid cabin class.")
