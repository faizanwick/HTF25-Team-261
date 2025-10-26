
def is_palindrome(s: str) -> bool:
    """
    Check if the provided string is a palindrome.
    
    Parameters:
    s (str): The string to check.

    Returns:
    bool: True if s is a palindrome, False otherwise.
    """
    # Normalize the string by removing non-alphanumeric characters and converting to lower case
    filtered_chars = ''.join(char for char in s if char.isalnum()).lower()
    
    # Check if the string is equal to its reverse
    return filtered_chars == filtered_chars[::-1]

# Example usage:
input_string = "A man, a plan, a canal, Panama"
print(f"The string '{input_string}' is a palindrome: {is_palindrome(input_string)}")
def my_function(param1, param2):
    """
    This is a sample function that takes two parameters and prints their sum.

    Parameters:
    param1 (int): The first parameter.
    param2 (int): The second parameter.

    Returns:
    int: The sum of param1 and param2.
    """
    result = param1 + param2
    return result

# Example of calling the function
result = my_function(5, 3)
print("The sum is:", result)