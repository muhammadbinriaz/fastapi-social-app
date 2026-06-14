class InsufficientFunds(Exception):
    pass


class BankAccount:
    def __init__(self, starting_balance: float = 0):
        self.balance = starting_balance

    def deposit(self, amount: float):
        self.balance += amount

    def withdraw(self, amount: float):
        if amount > self.balance:
            raise InsufficientFunds("Insufficient funds in account")
        self.balance -= amount

    def collect_interest(self):
        self.balance *= 1.1


def add(num1: float, num2: float) -> float:
    return num1 + num2


def subtract(num1: float, num2: float) -> float:
    return num1 - num2


def multiply(num1: float, num2: float) -> float:
    return num1 * num2


def divide(num1: float, num2: float) -> float:
    if num2 == 0:
        raise ZeroDivisionError("Cannot divide by zero")
    return num1 / num2
