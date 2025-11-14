import time

def decorator(func):
    def wrapper():
        print("Before calling the function.")
        func()
        time.sleep(3.5)
        print("After calling the function.")
    return wrapper

@decorator # Applying the decorator to a function
def greet():
    print("Hello, World!")


greet()