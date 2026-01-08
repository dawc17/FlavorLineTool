import json
from pathlib import Path

# Use a hidden folder in home directory for data storage using a JSON file
# This would be ~/.flavorlinetool/data.json for Unix-like systems
# and C:\Users\<User>\.flavorlinetool\data.json for Windows
DATA_FILE = Path.home() / ".flavorlinetool" / "data.json"

def _load_data():
    if not DATA_FILE.exists():
        return {"cookies": 0}
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return {"cookies": 0}

def _save_data(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def get_cookie_count() -> int:
    data = _load_data()
    return data.get("cookies", 0)

def set_cookie_count(count: int):
    data = _load_data()
    data["cookies"] = count
    _save_data(data)
