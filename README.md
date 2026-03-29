

# Restaurant Reservation System
### COIS-2020H — OOP Python Group Project

A command-line Hotel Reservation Management System built in Python using object-oriented programming principles including custom exceptions, dataclasses, inheritance, encapsulation, and a JSON-based persistence layer.

---

## Project Structure

```
├── Group2.py                 # Main program — all modules combined
├── Class Diagram.png         # UML class diagram of the system
├── README.md                 # Project documentation
├── users.json                # Auto-generated on first run
└── reservations.json         # Auto-generated on first run
```

---

## How to Run

Make sure all three `.py` files are in the same directory, then run:

```bash
python rest.py
```

No external libraries required — uses Python standard library only.

---

## Team Contributions

### Manisha — Exceptions & Data Entities
**File:** `exceptions_entities.py`

Responsible for the foundational layer of the program that all other modules depend on.

- Designed and implemented **5 custom exception classes** (`InvalidOptionError`, `EmptyFieldError`, `InvalidRegistrationChoiceError`, `InvalidReservationConfirmationError`, `InvalidDeletionChoiceError`), each inheriting from Python's built-in `Exception` class to enable structured `try/except` validation throughout the system
- Implemented the `Customer` dataclass using Python's `@dataclass` decorator, storing user credentials (email, first name, last name, password, date of birth) and a `verify_password()` method that encapsulates authentication logic
- Implemented the `Reservation` dataclass storing all booking details (email, number of days, check-in/out dates, number of persons, number of rooms), keeping data type-consistent and self-documenting across the system

---

### Gowtham — Storage Layer & System Core
**File:** `storage_system.py`

Responsible for all data persistence and the core system controller, including user authentication.

- Built the `StorageManager` class to handle all reading and writing to `users.json` and `reservations.json`, including a `_prepare_files()` method that initializes missing files on startup to prevent crashes on a fresh install
- Implemented `load_users()` using `**kwargs` unpacking to reconstruct `Customer` objects from JSON, and `save_user()` using `asdict()` from the `dataclasses` module to serialize objects back to disk — applying the single-responsibility principle by keeping storage logic separate from business logic
- Implemented `save_reservation()` and `delete_reservation()` methods with safe file read-modify-write cycles
- Built the `ReservationSystem` base class with `__init__` (instantiates `StorageManager`, tracks `active_user`), the reusable `_get_input()` helper (handles `EmptyFieldError` and `ValueError` in a loop), `register()` with duplicate-email detection and `InvalidRegistrationChoiceError` handling, and `login()` with password verification and a retry/register/exit recovery loop

---

### Darren — User Dashboard & Reservation Features
**File:** `reservation_features.py`

Responsible for all user-facing features after login, and the program's main entry point.

- Extended `ReservationSystem` via inheritance into `FullReservationSystem`, implementing `user_dashboard()` — a session loop that greets the user by name and routes to all five dashboard actions, with logout clearing `active_user` and returning to the main menu
- Implemented `view_res()` to display a formatted reservation using `str.replace()` and `title()` for clean key-name rendering, with graceful handling when no reservation exists
- Implemented `manage_res()` supporting both **Make** and **Modify** modes: Make mode collects all five fields and confirms with `InvalidReservationConfirmationError` on bad input; Modify mode displays current data as numbered fields, uses a `updated_data` working copy to prevent partial saves, and commits only on explicit save selection
- Implemented `cancel_res()` with a pre-check guard (skips prompt if no reservation exists), `Y/N` confirmation, and `InvalidDeletionChoiceError` for invalid input
- Wrote the `run()` entry point and `if __name__ == "__main__"` guard, tying all modules together into the final executable program

---

## OOP Concepts Demonstrated

| Concept | Where Applied |
|---------|--------------|
| Custom Exceptions | `exceptions_entities.py` — 5 domain-specific exception classes |
| Dataclasses | `Customer` and `Reservation` with auto-generated `__init__` and `__repr__` |
| Encapsulation | `verify_password()` inside `Customer`; `_get_input()` as a private helper |
| Single Responsibility | `StorageManager` handles only persistence; `ReservationSystem` handles only logic |
| Inheritance | `FullReservationSystem` extends `ReservationSystem` with dashboard features |
| Composition | `ReservationSystem` owns a `StorageManager` instance |
