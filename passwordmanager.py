import json
import os
import getpass
import hashlib
import base64
from dataclasses import dataclass, asdict
from secrets import choice
from termcolor import colored
from cryptography.fernet import Fernet

DB_FILE = "vault.json"
MASTER_FILE = "master.json"


# AES Encryption Setup

def generate_key(master_password: str) -> bytes:
    """Derive an AES encryption key from the master password using SHA256."""
    hashed = hashlib.sha256(master_password.encode()).digest()
    return base64.urlsafe_b64encode(hashed)
 
 
def encrypt_password(password: str, key: bytes) -> str:
    """Encrypt a password string using AES (Fernet)."""
    f = Fernet(key)
    return f.encrypt(password.encode()).decode()
 
 
def decrypt_password(encrypted_password: str, key: bytes) -> str:
    """Decrypt an AES encrypted password string."""
    f = Fernet(key)
    return f.decrypt(encrypted_password.encode()).decode()


# Master Password (SHA256 Hash)

def hash_password(password: str) -> str:
    """Hash a password string using SHA256."""
    return hashlib.sha256(password.encode()).hexdigest()
 
 
def save_master(master_password: str) -> None:
    """Hash and save the master password to master.json."""
    hashed = hash_password(master_password)
    with open(MASTER_FILE, "w") as f:
        json.dump({"master": hashed}, f)
 
 
def verify_master(master_password: str) -> bool:
    """Check if entered master password matches stored hash."""
    try:
        with open(MASTER_FILE, "r") as f:
            data = json.load(f)
        return hash_password(master_password) == data["master"]
    except FileNotFoundError:
        return False
 
 
def master_exists() -> bool:
    """Check if a master password has been created yet."""
    return os.path.isfile(MASTER_FILE)


# Data Model

@dataclass
class Credential:
    service: str
    username: str
    password: str


#  Data Helpers

def load_data(key: bytes) -> list:
    """Load and decrypt credentials from vault.json."""
    try:
        with open(DB_FILE, "r") as f:
            raw = json.load(f)
        credentials = []
        for entry in raw:
            decrypted = decrypt_password(entry["password"], key)
            credentials.append(Credential(
                service=entry["service"],
                username=entry["username"],
                password=decrypted
            ))
        return credentials
    except FileNotFoundError:
        return []
 
 
def save_data(credentials: list, key: bytes) -> None:
    """Encrypt and save credentials to vault.json."""
    encrypted_list = []
    for c in credentials:
        encrypted_list.append({
            "service": c.service,
            "username": c.username,
            "password": encrypt_password(c.password, key)
        })
    with open(DB_FILE, "w") as f:
        json.dump(encrypted_list, f, indent=4)
 



#  Add / Edit Credential  (option 1)

def add_or_update_credential(key: bytes) -> None:
    """Add a new credential or update an existing one."""
    service = input("Service name (e.g. github.com): ").strip()
    if not service:
        print(colored("Service name cannot be empty.", "red"))
        return add_or_update_credential(key)
 
    username = input("Username / email: ").strip()
    if not username:
        print(colored("Username cannot be empty.", "red"))
        return add_or_update_credential(key)
 
    password = getpass.getpass("Password (input hidden): ")
    if not password:
        print(colored("Password cannot be empty.", "red"))
        return add_or_update_credential(key)
 
    credentials = load_data(key)
 
    for cred in credentials:
        if cred.service.lower() == service.lower():
            confirm = input(colored(
                f"Entry for '{service}' already exists. Overwrite? (Y/N): ", "yellow"
            )).strip().lower()
            if confirm != "y":
                print(colored("Update cancelled.", "red"))
                return
            cred.username = username
            cred.password = password
            save_data(credentials, key)
            print(colored(f"✔ Updated credentials for {service}.", "green"))
            return
 
    credentials.append(Credential(service=service, username=username, password=password))
    save_data(credentials, key)
    print(colored(f"✔ Credentials for {service} saved.", "green"))


# Search and Retrieve Credentials (option 2)

def search_credential(key: bytes) -> None:
    """Search stored credentials by service name."""
    query = input("Search service name: ").strip().lower()
    if not query:
        print(colored("Search query cannot be empty.", "red"))
        return search_credential(key)
 
    credentials = load_data(key)
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
 
    reveal = input("\nEnter a result number to reveal its password (or press Enter to skip): ").strip()
    if reveal.isdigit():
        idx = int(reveal) - 1
        if 0 <= idx < len(matches):
            print(colored(f"\nPassword for {matches[idx].service}: {matches[idx].password}", "yellow"))
        else:
            print(colored("Invalid selection.", "red"))


# Delete Credential (option 3)

def delete_credential(key: bytes) -> None:
    """Remove a stored credential by service name."""
    credentials = load_data(key)
    if not credentials:
        print(colored("No credentials stored yet.", "red"))
        return
 
    service = input("Enter the service name to delete: ").strip()
    if not service:
        return delete_credential(key)
 
    original_count = len(credentials)
    credentials = [c for c in credentials if c.service.lower() != service.lower()]
 
    if len(credentials) == original_count:
        print(colored(f"No entry found for '{service}'.", "red"))
    else:
        save_data(credentials, key)
        print(colored(f"✔ Credentials for '{service}' deleted.", "green"))
 
 
#  List All Services (option 4)
 
def list_all_credentials(key: bytes) -> None:
    """Print every stored service and username (no passwords)."""
    credentials = load_data(key)
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
 
 
def run_menu(key: bytes) -> None:
    """Main loop — keeps showing the menu until the user exits."""
    while True:
        print_menu()
        choice = input("Enter a choice: ").strip()
 
        if choice == "1":
            add_or_update_credential(key)
        elif choice == "2":
            search_credential(key)
        elif choice == "3":
            delete_credential(key)
        elif choice == "4":
            list_all_credentials(key)
        elif choice == "5":
            print(colored("Goodbye!", "green"))
            break
        else:
            print(colored("Invalid choice. Please try again.", "red"))


# Master Password Authentication

def authenticate() -> str:
    """Handle first-time setup or returning user login.
    Returns the master password string on success."""
 
    if not master_exists():
        # Create a master password
        print(colored("\nWelcome! No master password found. Let's create one.", "green"))
        while True:
            master = getpass.getpass("Create a master password: ")
            confirm = getpass.getpass("Confirm master password: ")
            if master == confirm and master != "":
                save_master(master)
                print(colored("✔ Master password created. Please restart the program.", "green"))
                exit()
            else:
                print(colored("Passwords do not match or are empty. Try again.", "red"))
    else:
        # Verify master password for returning user 
        print(colored("\n🔒 Password Manager", "blue"))
        attempts = 0
        while attempts < 3:
            master = getpass.getpass("Enter your master password: ")
            if verify_master(master):
                print(colored("✔ Access granted.", "green"))
                return master
            else:
                attempts += 1
                remaining = 3 - attempts
                if remaining > 0:
                    print(colored(f"Incorrect password. {remaining} attempt(s) remaining.", "red"))
                else:
                    print(colored("Too many failed attempts. Exiting.", "red"))
                    exit()
 

# Entry Point

if __name__ == "__main__":
    master_password = authenticate()
    key = generate_key(master_password)
    run_menu(key)
