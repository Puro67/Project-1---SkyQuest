names_set = set()

while True:
    name = input("Enter a name (press Enter to stop): ")
    if name == "":
        print()
        break

    if name in names_set:
        print("Existing name")
    else:
        print("New name")
        names_set.add(name)

print("List of entered names:")
for name in names_set:
    print(name)