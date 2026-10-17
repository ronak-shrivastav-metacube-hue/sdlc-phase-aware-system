import json
import os
from typing import List, Dict, Any

class Storage:
    def __init__(self, filepath: str = "data/requests.json"):
        self.filepath = filepath
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Ensure the storage directory and file exist."""
        os.makedirs(os.path.dirname(self.filepath), exist_ok=True)
        if not os.path.exists(self.filepath):
            self.save_data([])

    def load_data(self) -> List[Dict[str, Any]]:
        """Load all requests from the JSON file."""
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            return []

    def save_data(self, data: List[Dict[str, Any]]) -> None:
        """Save all requests to the JSON file."""
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

    def append_record(self, record: Dict[str, Any]) -> None:
        """Append a single request record to storage."""
        data = self.load_data()
        data.append(record)
        self.save_data(data)