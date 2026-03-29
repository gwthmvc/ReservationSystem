import json
import os
from dataclasses import dataclass, asdict


# --- 1. Custom Exceptions ---
class InvalidOptionError(Exception):
    pass
class EmptyFieldError(Exception):
    pass
class InvalidRegistrationChoiceError(Exception):
    pass
class InvalidReservationConfirmationError(Exception):
    pass
class InvalidDeletionChoiceError(Exception):
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


@dataclass
class Reservation:
    email: str
    num_days: int
    from_date: str
    to_date: str
    num_persons: int
    num_rooms: int

class StorageManager:
    def __init__(self):
        self.user_file = "users.json"
        self.res_file = "reservations.json"
        self._prepare_files()

    def _prepare_files(self):
        for filename in [self.user_file, self.res_file]:
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                with open(filename, 'w') as f: json.dump({}, f)

    def load_users(self):
        with open(self.user_file, 'r') as f:
            data = json.load(f)
            return {e: Customer(**d) for e, d in data.items()}

    def save_user(self, customer):
        users_data = self.load_users() # Simplified for this block
        users_data[customer.email] = asdict(customer)
        with open(self.user_file, 'w') as f: json.dump(users_data, f, indent=4)

    def load_reservations(self):
        with open(self.res_file, 'r') as f: return json.load(f)

    def save_reservation(self, reservation):
        res_data = self.load_reservations()
        res_data[reservation.email] = asdict(reservation)
        with open(self.res_file, 'w') as f: json.dump(res_data, f, indent=4)

    def delete_reservation(self, email):
        res_data = self.load_reservations()
        if res_data.pop(email, None):
            with open(self.res_file, 'w') as f: json.dump(res_data, f, indent=4)

# --- Logic for ReservationSystem Class ---
def view_res(self):
    res = self.storage.load_reservations().get(self.active_user.email)
    if res:
        print(f"\n--- Current Reservation for {self.active_user.email} ---")
        for k, v in res.items(): print(f"{k.replace('_', ' ').title()}: {v}")
    else: print("\nNo reservation found")

def manage_res(self, mode):
    current_res = self.storage.load_reservations().get(self.active_user.email)
    if mode == "Modify" and not current_res:
        print("\nError: No existing reservation found to modify."); return

    fields = [("Number of days", "num_days", True), ("From Date", "from_date", False), 
              ("To Date", "to_date", False), ("Number of Persons", "num_persons", True), 
              ("Number of rooms", "num_rooms", True)]

    if mode == "Modify":
        updated_data = current_res.copy()
        while True:
            choice = input("\nEnter an option to modify (1-7): ")
            if choice in '12345':
                idx = int(choice) - 1
                label, key, is_num = fields[idx]
                updated_data[key] = self._get_input(f"Enter new {label}", is_num)
            elif choice == '6':
                self.storage.save_reservation(Reservation(**updated_data))
                print("Changes Saved!"); return
            elif choice == '7': return
    else:
        # 'Make' logic
        days = self._get_input("i. Number of days", True)
        # ... (rest of input gathering)
        self.storage.save_reservation(Reservation(self.active_user.email, days, "...", "...", 1, 1))

def cancel_res(self):
    res_data = self.storage.load_reservations()
    if self.active_user.email not in res_data:
        print("\nNo reservation found to cancel."); return
    choice = input("Confirm Delete? (Y/N): ").strip().upper()
    if choice == 'Y':
        self.storage.delete_reservation(self.active_user.email)
        print(">>> Reservation Deleted Successfully.")


# --- System Controller ---
class ReservationSystem:
    def _init_(self):
        self.storage = StorageManager()
        self.active_user = None

    def _get_input(self, prompt, is_numeric=False):
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                if not value: raise EmptyFieldError("Please fill all the data.")
                return int(value) if is_numeric else value
            except (EmptyFieldError, ValueError) as e: print(f"Error: {e}")

    def user_dashboard(self):
        while True:
            print(f"\n--- WELCOME, {self.active_user.fname.upper()} ---")
            print("a. View Reservation\nb. Make/Modify\ne. Cancel\nf. Logout")
            choice = input("Selection: ").lower()
            if choice == 'a': view_res(self)
            elif choice == 'b': manage_res(self, "Make")
            elif choice == 'e': cancel_res(self)
            elif choice == 'f': self.active_user = None; break

    def run(self):
        while True:
            print("\n=== MAIN MENU ===\na. Register\nb. Login\nc. Exit")
            choice = input("Selection: ").lower()
            if choice == 'a': register_user(self)
            elif choice == 'b': login_user(self)
            elif choice == 'c': break

if __name__ == "_main_":
    ReservationSystem().run()