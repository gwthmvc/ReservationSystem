import json
import os
from dataclasses import dataclass, asdict


class InvalidRegistrationChoiceError(Exception):
    pass
class InvalidOptionError:
    pass

@dataclass
class Customer:
    email: str
    fname: str
    lname: str
    password: str
    dob: str

    def verify_password(self, pwd):
        return self.password == pwd

def register_user(system):
    print("\n“Registration In-Process”")
    email = system._get_input("a. Email").lower()
    if email in system.storage.load_users():
        print("Account already exists!"); return

    fname = system._get_input("b. First Name")
    lname = system._get_input("c. Last Name")
    password = system._get_input("d. Password")
    dob = system._get_input("e. Date of Birth")

    while True:
        try:
            print("f. Submit\ng. Exit")
            choice = input("Selection: ").lower()
            if choice == 'f':
                new_cust = Customer(email, fname, lname, password, dob)
                system.storage.save_user(new_cust)
                print("Registration Successful!"); break
            elif choice == 'g':
                print("Registration aborted."); break
            else:
                raise InvalidRegistrationChoiceError("Enter only 'f' or 'g'.")
        except InvalidRegistrationChoiceError as e:
            print(f"Error: {e}")

def login_user(system):
    print("\n--- Login ---")
    email = input("Enter your Email: ").strip().lower()
    password = input("Enter your Password: ").strip()

    users = system.storage.load_users()
    user = users.get(email)

    if user and user.verify_password(password):
        system.active_user = user
        system.user_dashboard()
    else:
        print("\nThe password or username you've entered is incorrect")
        while True:
            try:
                choice = input("1. Try Again, 2. Register, 3. Exit: ")
                if choice == '1': login_user(system); break
                elif choice == '2': register_user(system); break
                elif choice == '3': break
                else: raise InvalidOptionError("Invalid choice.")
            except InvalidOptionError as e: print(e)