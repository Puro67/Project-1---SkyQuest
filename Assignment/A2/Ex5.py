total_talent = int (input ("Enter talent: "))
total_pound = int (input ("Enter pound: "))
total_lots = int (input ("Enter lots: "))
Total_in_grams = ((((total_talent * 20) + total_pound) * 32)+ total_lots) * 13.3
num_of_kg = Total_in_grams // 1000
num_of_grams = Total_in_grams % 1000
print ( f"The weight in modern unit {num_of_kg} kilograms and {num_of_grams} grams")