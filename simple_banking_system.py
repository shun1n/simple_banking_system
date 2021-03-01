import random
import sys
import sqlite3

used_card_numbers = []
user_accounts = []
numbers = [str(x) for x in range(10)]


class Account:
    number = None
    pin = None
    balance = 0

    def authorise(self, number, pin):
        self.number = number
        self.pin = pin


# is used for working with database
class Data:

    def __init__(self, db_conn, cur):
        self.db_conn = db_conn
        self.cur = cur

    def create_table(self):
        self.cur.execute("CREATE TABLE IF NOT EXISTS card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);")

    def commit(self):
        self.db_conn.commit()

def generate_number():
    IIN = "400000"
    # random card number generation
    remainder = "".join(random.choice(numbers) for _ in range(9))
    number = IIN + remainder
    number += "0"
    checksum = luhn_algorithm(number)
    if checksum:
        number = number[:-1] + checksum

    db.cur.execute(f'SELECT number FROM card WHERE number="{number}"')
    if cur.fetchone():
        return generate_number(db)  # regenerate number if it was found in existing numbers
    else:
        return number


def luhn_algorithm(number):
    luhn_sum = [int(x) for x in number]
    for i in range(0, 15, 2):
        luhn_sum[i] *= 2
        if luhn_sum[i] > 9:
            luhn_sum[i] -= 9
    luhn_sum = sum(luhn_sum[:-1])
    checksum = 0
    if luhn_sum % 10:
        checksum = 10 - (luhn_sum % 10)
    return str(checksum)


def create_account(db):
    number = generate_number()
    pin = "".join(random.choice(numbers) for _ in range(4))
    db.cur.execute(f"INSERT INTO card (number,pin) VALUES ({number}, {pin})")
    db.commit()
    print("Your card has been created\nYour card number:")
    print(number)
    print("Your card PIN:")
    print(pin)
    print()


def authorise_user(db, user):
    print("Enter your card number:")
    number = input(">")
    print("Enter your PIN:")
    pin = input(">")
    print()

    db.cur.execute(f'SELECT number, pin, balance FROM card WHERE number = "{number}"')
    response = db.cur.fetchone()
    if not response:
        return
    if response[1] == pin:
        user.number = response[0]
        user.pin = response[1]
        user.balance = response[2]
        print("You have successfully logged in!\n")
    else:
        return


def add_income(db, user):
    print("Enter income:")
    income = int(input(">"))
    print()
    user.balance += income
    db.cur.execute('UPDATE card SET balance = {} WHERE number = "{}";'.format(user.balance, user.number))
    db.commit()
    print("Income was added!\n")


def do_transfer(db, user):
    print("Transfer\nEnter card number:")
    transfer_to = input(">")
    if not validate_number(db, transfer_to, user):
        return 0
    print("Enter how much money you want to transfer:")
    amount = int(input(">"))
    if user.balance < amount:
        print("Not enough money!")
        return 0
    # *transaction validated*
    db.cur.execute('UPDATE card SET balance = balance + {} WHERE number = "{}";'.format(amount, transfer_to))
    db.cur.execute('UPDATE card SET balance = balance - {} WHERE number = "{}";'.format(amount, user.number))
    db.commit()
    user.balance -= amount
    print("Success!\n")



def validate_number(db, card_number, user):
    if len(card_number) != 16:
        print("Probably you made a mistake in the card number. Please try again!\n")
    elif user.number == card_number:
        print("You can't transfer money to the same account!\n")
        return 0
    elif card_number[-1] != luhn_algorithm(card_number):
        print(card_number[-1], luhn_algorithm(card_number))
        print("Probably you made a mistake in the card number. Please try again!\n")
        return 0
    db.cur.execute(f"SELECT number FROM card WHERE number = {card_number}")
    r = db.cur.fetchone()
    if not r:
        print("Such a card does not exist.\n")
        return 0
    if r[0] != card_number:
        print("Such a card does not exist.\n")
        return 0
    return 1


def close_account(db, user):
    db.cur.execute("DELETE FROM card WHERE number = {}".format(user.number))
    db.commit()
    user.number = None
    user.pin = None
    user.balance = 0
    print("The account has been closed!\n")



# prints user interface and handles inputs
def call_interface(db):
    main_menu = ["1. Create an account", "2. Log into account", "0. Exit"]
    account_menu = ["1. Balance", "2. Add income", "3. Do transfer", "4. Close account", "5. Log out", "0. Exit"]
    user = Account()
    while True:
        if not user.number:
            for item in main_menu:
                print(item)
            choice = input(">")
            print()
            if choice not in list("012"):
                print("Incorrect input\n")
                continue
            choice = int(choice)
            if choice == 0:
                print("Bye!")
                sys.exit()
            elif choice == 1:
                create_account(db)
                continue
            elif choice == 2:
                authorise_user(db, user)
                if not user.number:
                    print("\nWrong card number or PIN!\n")
                continue
        else:
            for item in account_menu:
                print(item)
            choice = input(">")
            print()
            if choice not in list("012345"):
                print("Incorrect input\n")
                continue
            choice = int(choice)
            if choice == 0:
                print("Bye!")
                sys.exit()
            elif choice == 1:
                print("Balance:", user.balance)
            elif choice == 2:
                add_income(db, user)
            elif choice == 3:
                do_transfer(db, user)
            elif choice == 4:
                close_account(db, user)
            else:
                user.number = None
                user.pin = None
                user.balance = 0
                print("You have successfully logged out!\n")
                continue


if __name__ == "__main__":
    db_conn = sqlite3.connect("card.s3db")
    cur = db_conn.cursor()
    db = Data(db_conn, cur)
    db.create_table()
    call_interface(db)

    db.commit()
