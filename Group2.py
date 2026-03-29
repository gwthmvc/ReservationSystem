import json
import os
from dataclasses import dataclass, asdict
from getpass import getpass

# --- 1. Custom Exceptions ---
class InvalidOptionError(Exception):
    """Raised when a user enters an option not in the menu."""
    pass

class EmptyFieldError(Exception):
    """Raised when a required input field is left blank."""
    pass

class InvalidRegistrationChoiceError(Exception):
    """Raised when user enters something other than 'f' or 'g' during signup."""
    pass

class InvalidReservationConfirmationError(Exception):
    """Raised when user enters something other than 'R' or 'Q' during reservation."""
    pass

class InvalidDeletionChoiceError(Exception):
    """Raised when user enters something other than 'Y' or 'N' during cancellation."""
    pass

# --- 2. Data Classes (Entities) ---
@dataclass
class Customer:
    email: str
    fname: str
    lname: str
    password: str
    dob: str

    def verify_password(self, pwd):
        return self.password == pwd

@dataclass
class Reservation:
    email: str
    num_days: int
    from_date: str
    to_date: str
    num_persons: int
    num_rooms: int

# --- 3. Persistence Layer (Storage Manager) ---
class StorageManager:
    def __init__(self):
        self.user_file = "users.json"
        self.res_file = "reservations.json"
        self._prepare_files()

    def _prepare_files(self):
        """Ensures files exist and are not empty."""
        for filename in [self.user_file, self.res_file]:
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                with open(filename, 'w') as f:
                    json.dump({}, f)

    def load_users(self):
        with open(self.user_file, 'r') as f:
            data = json.load(f)
            return {e: Customer(**d) for e, d in data.items()}

    def save_user(self, customer):
        with open(self.user_file, 'r') as f:
            users_data = json.load(f)
        users_data[customer.email] = asdict(customer)
        with open(self.user_file, 'w') as f:
            json.dump(users_data, f, indent=4)

    def load_reservations(self):
        with open(self.res_file, 'r') as f:
            return json.load(f)

    def save_reservation(self, reservation):
        res_data = self.load_reservations()
        res_data[reservation.email] = asdict(reservation)
        with open(self.res_file, 'w') as f:
            json.dump(res_data, f, indent=4)

    def delete_reservation(self, email):
        res_data = self.load_reservations()
        if res_data.pop(email, None):
            with open(self.res_file, 'w') as f:
                json.dump(res_data, f, indent=4)

# --- 4. System Controller (The Logic) ---
class ReservationSystem:
    def __init__(self):
        self.storage = StorageManager()
        self.active_user = None

    def _get_input(self, prompt, is_numeric=False):
        """Persistent input helper with type validation."""
        while True:
            try:
                value = input(f"{prompt}: ").strip()
                if not value:
                    raise EmptyFieldError("Please fill all the data for registration.")
                return int(value) if is_numeric else value
            except EmptyFieldError as e:
                print(f"Error: {e}")
            except ValueError:
                print("Error: Please enter a whole number.")

    def register(self):
        print("\n“Registration In-Process”")
        email = self._get_input("a. Email").lower()
        if email in self.storage.load_users():
            print("Account already exists!"); return

        fname = self._get_input("b. First Name")
        lname = self._get_input("c. Last Name")
        password = getpass("d. Password")
        dob = self._get_input("e. Date of Birth")

        while True:
            try:
                print("f. Submit\ng. Exit")
                choice = input("Selection: ").lower()
                if choice == 'f':
                    new_cust = Customer(email, fname, lname, password, dob)
                    self.storage.save_user(new_cust)
                    print("Registration Successful!"); break
                elif choice == 'g':
                    print("Registration aborted."); break
                else:
                    raise InvalidRegistrationChoiceError("Enter only 'f' or 'g'.")
            except InvalidRegistrationChoiceError as e:
                print(f"Error: {e}")

    def login(self):
        print("\n--- Login ---")
        email = input("Enter your Email: ").strip().lower()
        password = getpass("Enter your Password: ").strip()

        users = self.storage.load_users()
        user = users.get(email)

        if user and user.verify_password(password):
            self.active_user = user
            self.user_dashboard()
        else:
            print("\nThe password or username you've entered is incorrect")
            while True:
                try:
                    choice = input("1. Try Again, 2. Register, 3. Exit: ")
                    if choice == '1': self.login(); break
                    elif choice == '2': self.register(); break
                    elif choice == '3': break
                    else: raise InvalidOptionError("Invalid choice.")
                except InvalidOptionError as e: print(e)

    def user_dashboard(self):
        while True:
            print(f"\n--- WELCOME, {self.active_user.fname.upper()} ---")
            print("a. View Reservation\nb. Make Reservation\nd. Modify Reservation")
            print("e. Cancel Reservation\nf. Logout")
            
            choice = input("Selection: ").lower()
            if choice == 'a': self.view_res()
            elif choice in ['b', 'd']: self.manage_res("Make" if choice == 'b' else "Modify")
            elif choice == 'e': self.cancel_res()
            elif choice == 'f': self.active_user = None; break
            else: print("Invalid menu choice.")

    def view_res(self):
        res = self.storage.load_reservations().get(self.active_user.email)
        if res:
            print(f"\n--- Current Reservation for {self.active_user.email} ---")
            for k, v in res.items(): print(f"{k.replace('_', ' ').title()}: {v}")
        else:
            print("\nNo reservation found")

    def manage_res(self, mode):
        # 1. Load existing data if modifying
        current_res = self.storage.load_reservations().get(self.active_user.email)
        
        if mode == "Modify" and not current_res:
            print("\nError: No existing reservation found to modify."); return

        # 2. Define our fields for easy mapping
        # Format: (Display Name, Dict Key, Is Numeric)
        fields = [
            ("Number of days", "num_days", True),
            ("From Date", "from_date", False),
            ("To Date", "to_date", False),
            ("Number of Persons", "num_persons", True),
            ("Number of rooms", "num_rooms", True)
        ]

        if mode == "Modify":
            print("\n--- Current Reservation Data ---")
            for i, (label, key, _) in enumerate(fields, 1):
                print(f"{i}. {label}: {current_res[key]}")
            
            print("6. Save and Exit")
            print("7. Cancel changes")

            # Create a working copy so we don't save until they confirm 'R'
            updated_data = current_res.copy()

            while True:
                choice = input("\nEnter an option to modify (1-7): ")
                
                if choice in ['1', '2', '3', '4', '5']:
                    idx = int(choice) - 1
                    label, key, is_num = fields[idx]
                    new_val = self._get_input(f"Enter new {label}", is_num)
                    updated_data[key] = new_val
                    print(f">> Updated {label} to: {new_val}")
                
                elif choice == '6':
                    # Save logic
                    new_res = Reservation(**updated_data)
                    self.storage.save_reservation(new_res)
                    print("\nChanges Saved Successfully!")
                    return
                
                elif choice == '7':
                    print("Modification cancelled.")
                    return
                else:
                    print("Invalid selection. Please choose 1-7.")

        else:
            # --- Standard 'Make' Reservation Flow ---
            print(f"\n--- {mode} Reservation ---")
            days = self._get_input("i. Number of days", True)
            start = self._get_input("ii. From Date")
            end = self._get_input("iii. To Date")
            people = self._get_input("iv. Number of Persons", True)
            rooms = self._get_input("v. Number of rooms", True)

            while True:
                try:
                    print("\nvi. Reserve")
                    confirm = input("Type 'R' to Reserve or 'Q' to Quit: ").upper()
                    if confirm == 'R':
                        new_res = Reservation(self.active_user.email, days, start, end, people, rooms)
                        self.storage.save_reservation(new_res)
                        print("Reservation Saved Successfully!"); break
                    elif confirm == 'Q':
                        print("Process cancelled."); break
                    else:
                        raise InvalidReservationConfirmationError("Enter 'R' or 'Q'.")
                except InvalidReservationConfirmationError as e: print(f"Error: {e}")

    def cancel_res(self):
        # Check if a reservation even exists before asking to delete
        res_data = self.storage.load_reservations()
        if self.active_user.email not in res_data:
            print("\nNo reservation found to cancel.")
            return

        while True:
            try:
                print(f"\nCAUTION: Are you sure you want to delete the reservation for {self.active_user.email}?")
                choice = input("Confirm Delete? (Y/N): ").strip().upper()

                if choice == 'Y':
                    self.storage.delete_reservation(self.active_user.email)
                    print(">>> Reservation Deleted Successfully.")
                    break
                elif choice == 'N':
                    print(">>> Cancellation aborted. Your reservation is safe.")
                    break
                else:
                    raise InvalidDeletionChoiceError("Please enter only 'Y' for Yes or 'N' for No.")
            
            except InvalidDeletionChoiceError as e:
                print(f"Error: {e}")

    def run(self):
        print("*********************************************\n* Welcome to the Object Reservation System  *\n*********************************************")
        while True:
            print("\n=== MAIN MENU ===\na. Register/signup\nb. Login\nc. Exit")
            choice = input("Selection: ").lower()
            if choice == 'a': self.register()
            elif choice == 'b': self.login()
            elif choice == 'c': 
                print("\nThank you for using our Reservation System"); break
            else: print("Invalid choice. Select a, b, or c.")

if __name__ == "__main__":
    ReservationSystem().run()