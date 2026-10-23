sex = str( input("Enter your biological sex: "))
hemoglobin = int( input("Enter your and hemoglobin value in (g/l): "))
if sex in ["male", "Male"]:
    if hemoglobin < 117:
        print ("Your hemoglobin is low.")
    elif 117 >= hemoglobin <= 155:
        print ("Your hemoglobin is normal.")
    elif hemoglobin > 155:
        print ("Your hemoglobin is high.")
if sex in ["female", "Female"]:
    if hemoglobin < 134:
        print ("Your hemoglobin is low.")
    elif 134 >= hemoglobin <= 167:
        print ("Your hemoglobin is normal.")
    elif hemoglobin > 167:
        print ("Your hemoglobin is high.")