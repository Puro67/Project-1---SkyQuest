num_list = []
def sum_of_numbers(num_list):
    return (sum(num_list))
numbers = input("Enter a number(Use 'Enter' to stop): ")
while numbers != '':
    num_list.append(int(numbers))
    numbers = input("Enter a number(Use 'Enter' to stop): ")
total_sum = sum_of_numbers(num_list)

print(f"Your list of numbers: {num_list}")
print(f"The sum of all numbers is: {total_sum}")
