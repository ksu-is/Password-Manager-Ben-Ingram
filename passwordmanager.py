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
