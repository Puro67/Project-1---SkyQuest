nums = []
numbers = input("Enter a number(or 'Enter' to stop): ")
while numbers != '':
    nums.append(int(numbers))
    numbers = input("Enter a number(or 'Enter' to stop): ")

def list_even_numbers(nums):
    even_list = []
    for numbers in nums:
     if numbers % 2 == 0:
        even_list.append(numbers)
    return even_list
final_even_list = list_even_numbers(nums)
print(f"The list of numbers is {nums}")
print(f"The list of even numbers is: {final_even_list}")