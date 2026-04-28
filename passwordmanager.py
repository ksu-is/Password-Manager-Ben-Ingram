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
