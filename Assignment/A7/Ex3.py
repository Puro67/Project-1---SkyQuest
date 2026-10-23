airports = {}

while True:
    print("--- Airport Database Menu ---")
    print("1. Enter a new airport")
    print("2. Fetch airport information")
    print("3. Quit")

    choice = input("Choose an option (1, 2, or 3): ")

    if choice == "1":
        icao = input("Enter the ICAO code: ").upper()
        name = input("Enter the airport name: ")
        airports[icao] = name
        print(f"Successfully added {name} ({icao}).")

    elif choice == "2":
        icao = input("Enter the ICAO code to fetch: ").upper()
        if icao in airports:
            print(f"The airport name for {icao} is: {airports[icao]}")
        else:
            print("Airport not found in the database.")

    elif choice == "3":
        print("Exiting program. Goodbye!")
        break

    else:
        print("Invalid choice. Please enter 1, 2, or 3.")