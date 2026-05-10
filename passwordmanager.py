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


# Search and Retrieve Credentials (option 2)

def search_credential() -> None:
    """Search stored credentials by service name (partial match supported)."""
    query = input("Search service name: ").strip().lower()
    if not query:
        print(colored("Search query cannot be empty.", "red"))
        return search_credential()

    credentials = load_data()
    matches = []
    for c in credentials:
        if query in c.service.lower():
            matches.append(c)

    if not matches:
        print(colored(f"No credentials found matching '{query}'.", "red"))
        return

    print(colored(f"\nFound {len(matches)} result(s):\n", "yellow"))
    for i, cred in enumerate(matches, start=1):
        print(colored(f"  [{i}] Service:  {cred.service}", "cyan"))
        print(colored(f"      Username: {cred.username}", "cyan"))
        print(colored(f"      Password: {'*' * len(cred.password)}", "cyan"))

    # Let the user reveal a specific password
    reveal = input("\nEnter a result number to reveal its password (or press Enter to skip): ").strip()
    if reveal.isdigit():
        idx = int(reveal) - 1
        if 0 <= idx < len(matches):
            print(colored(f"\nPassword for {matches[idx].service}: {matches[idx].password}", "yellow"))
        else:
            print(colored("Invalid selection.", "red"))


# Delete Credential (option 3)

def delete_credential() -> None:
    """Remove a stored credential by service name."""
    credentials = load_data()
    if not credentials:
        print(colored("No credentials stored yet.", "red"))
        return

    service = input("Enter the service name to delete: ").strip()
    if not service:
        return delete_credential()

    original_count = len(credentials)
    credentials = [c for c in credentials if c.service.lower() != service.lower()]

    if len(credentials) == original_count:
        print(colored(f"No entry found for '{service}'.", "red"))
    else:
        save_data(credentials)
        print(colored(f"✔ Credentials for '{service}' deleted.", "green"))


# List All Services (option 4)

def list_all_credentials() -> None:
    """Print every stored service name (no passwords)."""
    credentials = load_data()
    if not credentials:
        print(colored("No credentials stored yet.", "yellow"))
        return

    print(colored(f"\nStored services ({len(credentials)} total):", "yellow"))
    for cred in credentials:
        print(colored(f"  • {cred.service}  ({cred.username})", "cyan"))
    print()


# CLI Menu

def print_menu() -> None:
    print(colored("\n" + "─" * 40, "blue"))
    print(colored("       🔒 Password Manager", "blue"))
    print(colored("─" * 40, "blue"))
    print(colored("  1) Add / Update a credential", "cyan"))
    print(colored("  2) Search / Retrieve a credential", "cyan"))
    print(colored("  3) Delete a credential", "cyan"))
    print(colored("  4) List all services", "cyan"))
    print(colored("  5) Exit", "red"))
    print(colored("─" * 40 + "\n", "blue"))


def run_menu() -> None:
    while True:
        print_menu()
        choice = input("Enter a choice: ").strip()
        if choice == "1":
            add_or_update_credential()
        elif choice == "2":
            search_credential()
        elif choice == "3":
            delete_credential()
        elif choice == "4":
            list_all_credentials()
        elif choice == "5":
            print(colored("Goodbye!", "green"))
            break
        else:
            print(colored("Invalid choice. Please try again.", "red"))


# Entry Point

if __name__ == "__main__":
    run_menu()
