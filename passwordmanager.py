import json
import os
from dataclasses import dataclass, asdict
from getpass import getpass

DB_FILE = "vault.json"


@dataclass
class Credential:
    service: str
    username: str
    password: str
def load_data():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return []


def save_data(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=4)

# Helper Functions 

def load_data() -> list[Credential]:
    """Load vault and return a list of Credential objects."""
    try:
        with open(DB_FILE, "r") as f:
            raw = json.load(f)
        return [Credential(**entry) for entry in raw]
    except FileNotFoundError:
        return []
 
 
def save_data(credentials: list[Credential]) -> None:
    """Persist a list of Credential objects to disk."""
    with open(DB_FILE, "w") as f:
        json.dump([asdict(c) for c in credentials], f, indent=4

#  Credential adding/editing
 
def add_or_update_credential() -> None:
    """Add a new credential or update an existing one for the same service."""
    service = input("Service name (e.g. github.com): ").strip()
    if not service:
        print(colored("Service name cannot be empty.", "red"))
        return add_or_update_credential()
 
    username = input("Username / email: ").strip()
    if not username:
        print(colored("Username cannot be empty.", "red"))
        return add_or_update_credential()
 
    password = getpass.getpass("Password (input hidden): ")
    if not password:
        print(colored("Password cannot be empty.", "red"))
        return add_or_update_credential()
 
    credentials = load_data()
 
    # Check if an entry already exists
    for cred in credentials:
        if cred.service.lower() == service.lower():
            confirm = input(
                colored(
                    f"Entry for '{service}' already exists. Overwrite? (Y/N): ",
                    "yellow",
                )
            ).strip().lower()
            if confirm != "y":
                print(colored("Update cancelled.", "red"))
                return
            cred.username = username
            cred.password = password
            save_data(credentials)
            print(colored(f"✔ Updated credentials for {service}.", "green"))
            return
 
    # New entry
    credentials.append(Credential(service=service, username=username, password=password))
    save_data(credentials)
    print(colored(f"✔ Credentials for {service} saved.", "green"))
