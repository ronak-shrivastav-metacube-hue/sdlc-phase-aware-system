from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Tuple
from src.storage import Storage

@dataclass
class FeatureRequest:
    id: str
    description: str
    client: str
    project: str
    timestamp: str

class RequestHandler:
    def __init__(self, storage: Storage):
        self.storage = storage

    def validate_description(self, description: str) -> Tuple[bool, str]:
        """Validate description is between 10 and 500 characters."""
        desc_len = len(description.strip())
        if desc_len < 10:
            return False, "Description is too short (minimum 10 characters required)."
        if desc_len > 500:
            return False, "Description is too long (maximum 500 characters allowed)."
        return True, ""

    def add_request(self, description: str, client: str, project: str) -> Tuple[bool, str]:
        """Validate input, generate ID & timestamp, and persist the request."""
        is_valid, err_msg = self.validate_description(description)
        if not is_valid:
            return False, err_msg

        existing_requests = self.storage.load_data()
        new_id = str(len(existing_requests) + 1)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        req = FeatureRequest(
            id=new_id,
            description=description.strip(),
            client=client.strip() or "Unknown Client",
            project=project.strip() or "General Project",
            timestamp=timestamp
        )

        self.storage.append_record(asdict(req))
        return True, f"Successfully created request #{new_id}!"

    def get_all_requests(self) -> list[Dict[str, Any]]:
        """Retrieve all stored requests."""
        return self.storage.load_data()