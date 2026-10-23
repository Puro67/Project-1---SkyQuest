seasons = ("winter", "winter",
           "spring", "spring", "spring",
           "summer", "summer", "summer",
           "autumn", "autumn", "autumn", "winter")

month = int(input("Enter the number of a month (1-12): "))

if 1 <= month <= 12:
    season = seasons[month - 1]
    print(f"The corresponding season is: {season}")
else:
    print("Invalid month number. Please enter a number between 1 and 12.")