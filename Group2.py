
# Gowtham Velicheti 0892430
# Darren Billy
# Manisha Chettri 0893617

# Import required libraries
import json                 # Used to read and write JSON files
import os                   # Used to check if files exist
from dataclasses import dataclass, asdict   # Used for creating simple classes and converting to dictionaries
from getpass import getpass # Used to hide password input


# --- 1. Custom Exceptions ---
# These are custom errors I created to handle invalid user inputs

class InvalidOptionError(Exception):
    """This error is used when the user selects an option that doesn’t exist."""
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
# These classes just store user and reservation data

@dataclass
class Customer:
    email: str       # user's email
    fname: str       # First name
    lname: str       # Last name
    password: str    # Password
    dob: str         # Date of birth

    # Checks if the entered password matches the saved one (used during login)
    def verify_password(self, pwd):
        return self.password == pwd


@dataclass
class Reservation:
    email: str           # User email (used as key)
    num_days: int        # Number of days booked
    from_date: str       # Start date
    to_date: str         # End date
    num_persons: int     # Number of guests
    num_rooms: int       # Number of rooms


# --- 3. Persistence Layer (Storage Manager) ---
# This class handles reading and writing data to files

class StorageManager:

    def __init__(self):
        # File names for storing data
        self.user_file = "users.json"
        self.res_file = "reservations.json"

        # Make sure files exist before using them
        self._prepare_files()

    def _prepare_files(self):
        """Ensures files exist and are not empty."""

        # Loop through both files
        for filename in [self.user_file, self.res_file]:

            # If file does not exist OR is empty
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:

                # Create file and write empty dictionary
                with open(filename, 'w') as f:
                    json.dump({}, f)

    def load_users(self):
        # Open users file and load data
        with open(self.user_file, 'r') as f:
            data = json.load(f)

            # Convert dictionary data into Customer objects
            return {e: Customer(**d) for e, d in data.items()}

    def save_user(self, customer):
        # Load existing users
        with open(self.user_file, 'r') as f:
            users_data = json.load(f)

        # Add or update user using email as key
        users_data[customer.email] = asdict(customer)

        # Save updated data back to file
        with open(self.user_file, 'w') as f:
            json.dump(users_data, f, indent=4)

    def load_reservations(self):
        # Load reservation data from file
        with open(self.res_file, 'r') as f:
            return json.load(f)

    def save_reservation(self, reservation):
        # Load existing reservations
        res_data = self.load_reservations()

        # Add or update reservation
        res_data[reservation.email] = asdict(reservation)

        # Save updated reservations
        with open(self.res_file, 'w') as f:
            json.dump(res_data, f, indent=4)

    def delete_reservation(self, email):
        # Load reservations
        res_data = self.load_reservations()

        # Remove reservation if it exists
        if res_data.pop(email, None):

            # Save updated data
            with open(self.res_file, 'w') as f:
                json.dump(res_data, f, indent=4)


# --- 4. System Controller (Main Logic) ---
# This class controls the program flow and user interaction

class ReservationSystem:

    def __init__(self):
        # Create storage manager
        self.storage = StorageManager()

        # No user logged in at start
        self.active_user = None


#_get_input method


    def _get_input(self, prompt, is_numeric=False):
        """Takes input from the user and makes sure it's valid before continuing."""

        while True:
            try:
                # take input and remove extra spaces
                value = input(f"{prompt}: ").strip()

                # if user leaves it blank, show error
                if not value:
                    raise EmptyFieldError("Please fill all the data for registration.")

                # convert to number if this input should be numeric
            
                if is_numeric:
                    if not value.isdigit():
                        raise ValueError("Only numbers allowed")
                    return int(value)

                return value

            except EmptyFieldError as e:
                print(f"Error: {e}")

            except ValueError:
                print("Error: Please enter a whole number.")

    def _validate_email(self, value):
        if "@" not in value or "." not in value.split("@")[-1]:
            raise EmptyFieldError("Invalid email format. Must contain '@' and a domain.")

    def _validate_name(self, value):
        if not value.replace("-", "").replace("'", "").isalpha():
            raise EmptyFieldError("Name must contain letters only.")

    def _validate_dob(self, value):
        parts = value.split("-")
        if len(parts) != 3 or not all(p.isdigit() for p in parts):
            raise EmptyFieldError("Date of Birth must be in YYYY-MM-DD format.")

    def register(self):
        print("\n“Registration In-Process”")

        # Get email
        while True:
            email = self._get_input("a. Email").lower()
            try:
                self._validate_email(email)
                break
            except EmptyFieldError as e:
                print(f"Error: {e}")

        # Check if account already exists
        if email in self.storage.load_users():
            print("Account already exists!")
            return

        # Get user details
        while True:
            fname = self._get_input("b. First Name")
            try:
                self._validate_name(fname)
                break
            except EmptyFieldError as e:
                print(f"Error: {e}")

        while True:
            lname = self._get_input("c. Last Name")
            try:
                self._validate_name(lname)
                break
            except EmptyFieldError as e:
                print(f"Error: {e}")

        password = getpass("d. Password")  # Hidden input

        while True:
            dob = self._get_input("e. Date of Birth(YYYY-MM-DD)")
            try:
                self._validate_dob(dob)
                break
            except EmptyFieldError as e:
                print(f"Error: {e}")

        # Confirm or exit
        while True:
            try:
                print("f. Submit\ng. Exit")
                choice = input("Selection: ").lower()

                if choice == 'f':
                    # Create Customer object
                    new_cust = Customer(email, fname, lname, password, dob)

                    # Save user to file
                    self.storage.save_user(new_cust)

                    print("Registration Successful!")
                    break

                elif choice == 'g':
                    print("Registration aborted.")
                    break

                else:
                    raise InvalidRegistrationChoiceError("Enter only 'f' or 'g'.")

            except InvalidRegistrationChoiceError as e:
                print(f"Error: {e}")

    def login(self):
        print("\n--- Login ---")

        # Get login details
        email = input("Enter your Email: ").strip().lower()
        password = getpass("Enter your Password: ").strip()

        # Load users and find user
        users = self.storage.load_users()
        user = users.get(email)

        # Check credentials
        if user and user.verify_password(password):
            self.active_user = user
            self.user_dashboard()
        else:
            print("\nThe password or username you've entered is incorrect")

            # Retry options
            while True:
                try:
                    choice = input("1. Try Again, 2. Register, 3. Exit: ")

                    if choice == '1':
                        self.login()
                        break
                    elif choice == '2':
                        self.register()
                        break
                    elif choice == '3':
                        break
                    else:
                        raise InvalidOptionError("Invalid choice.")

                except InvalidOptionError as e:
                    print(e)

    def user_dashboard(self):
        # Keep running until logout
        while True:
            print(f"\n--- WELCOME, {self.active_user.fname.upper()} ---")

            # Display menu
            print("a. View Reservation\nb. Make Reservation\nd. Modify Reservation")
            print("e. Cancel Reservation\nf. Logout")

            choice = input("Selection: ").lower()

            if choice == 'a':
                self.view_res()
            elif choice in ['b', 'd']:
                self.manage_res("Make" if choice == 'b' else "Modify")
            elif choice == 'e':
                self.cancel_res()
            elif choice == 'f':
                self.active_user = None  # Logout
                break
            else:
                print("Invalid menu choice.")

    def view_res(self):
        # Get reservation for logged-in user
        res = self.storage.load_reservations().get(self.active_user.email)

        if res:
            print(f"\n--- Current Reservation for {self.active_user.email} ---")

            # Print each field
            for k, v in res.items():
                print(f"{k.replace('_', ' ').title()}: {v}")
        else:
            print("\nNo reservation found")

    def manage_res(self, mode):
        # Load existing reservation
        current_res = self.storage.load_reservations().get(self.active_user.email)

        # If modifying but no reservation exists
        if mode == "Modify" and not current_res:
            print("\nError: No existing reservation found to modify.")
            return

        # Define fields for reservation
        fields = [
            ("Number of days", "num_days", True),
            ("From Date", "from_date", False),
            ("To Date", "to_date", False),
            ("Number of Persons", "num_persons", True),
            ("Number of rooms", "num_rooms", True)
        ]

        # MODIFY MODE
        if mode == "Modify":
            print("\n--- Current Reservation Data ---")

            # Display current values
            for i, (label, key, _) in enumerate(fields, 1):
                print(f"{i}. {label}: {current_res[key]}")

            print("6. Save and Exit")
            print("7. Cancel changes")

            # Copy data to avoid overwriting immediately
            updated_data = current_res.copy()

            while True:
                choice = input("\nEnter an option to modify (1-7): ")

                if choice in ['1', '2', '3', '4', '5']:
                    idx = int(choice) - 1
                    label, key, is_num = fields[idx]

                    # Get new value
                    new_val = self._get_input(f"Enter new {label}", is_num)

                    # Update value
                    updated_data[key] = new_val

                    print(f">> Updated {label} to: {new_val}")

                elif choice == '6':
                    # Save changes
                    new_res = Reservation(**updated_data)
                    self.storage.save_reservation(new_res)

                    print("\nChanges Saved Successfully!")
                    return

                elif choice == '7':
                    print("Modification cancelled.")
                    return

                else:
                    print("Invalid selection. Please choose 1-7.")

        # MAKE MODE
        else:
            print(f"\n--- {mode} Reservation ---")

            # Get reservation details
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

                        print("Reservation Saved Successfully!")
                        break

                    elif confirm == 'Q':
                        print("Process cancelled.")
                        break

                    else:
                        raise InvalidReservationConfirmationError("Enter 'R' or 'Q'.")

                except InvalidReservationConfirmationError as e:
                    print(f"Error: {e}")

    def cancel_res(self):
        # Load reservation data
        res_data = self.storage.load_reservations()

        # Check if reservation exists
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
        # Display welcome message
        print("\n*********************************************")
        print("* Welcome to the Object Reservation System  *")
        print("*********************************************")

        # Main menu loop
        while True:
            print("\n=== MAIN MENU ===\n\na. Register/signup\nb. Login\nc. Exit\n")

            choice = input("Selection: ").lower()

            if choice == 'a':
                self.register()
            elif choice == 'b':
                self.login()
            elif choice == 'c':
                print("\nThank you for using our Reservation System")
                break
            else:
                print("Invalid choice. Select a, b, or c.")


# Run the program
if __name__ == "__main__":
    ReservationSystem().run()