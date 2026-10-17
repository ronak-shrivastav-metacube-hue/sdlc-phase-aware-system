import re
import time

class SecurityGuard:
    def __init__(self, rate_limit_seconds: float = 2.0):
        self.last_call_time = 0.0
        self.rate_limit_seconds = rate_limit_seconds

    def sanitize_input(self, text: str) -> str:
        """Basic sanitization: strip HTML tags, normalize whitespace, remove unsafe chars."""
        if not text:
            return ""
        # Remove HTML tags to prevent injection
        clean_text = re.sub(r'<[^>]*>', '', text)
        # Normalize multiple spaces/newlines into single spaces
        clean_text = ' '.join(clean_text.split())
        return clean_text.strip()

    def validate_and_sanitize(self, description: str, client: str, project: str) -> tuple[bool, str, dict]:
        """Validate input length, sanitize text, and enforce rate limiting."""
        # 1. Sanitize inputs
        clean_desc = self.sanitize_input(description)
        clean_client = self.sanitize_input(client)
        clean_project = self.sanitize_input(project)

        # 2. Length validation
        if len(clean_desc) < 10:
            return False, "Description is too short (minimum 10 characters required).", {}
        if len(clean_desc) > 500:
            return False, "Description is too long (maximum 500 characters allowed).", {}
        
        if len(clean_client) > 100:
            return False, "Client name is too long (maximum 100 characters allowed).", {}
        
        if len(clean_project) > 100:
            return False, "Project name is too long (maximum 100 characters allowed).", {}

        # 3. Rate limiting check
        current_time = time.time()
        elapsed = current_time - self.last_call_time
        if elapsed < self.rate_limit_seconds:
            wait_time = round(self.rate_limit_seconds - elapsed, 1)
            return False, f"Rate limit active! Please wait {wait_time}s before submitting another request.", {}

        self.last_call_time = current_time

        sanitized_data = {
            "description": clean_desc,
            "client": clean_client or "Unknown Client",
            "project": clean_project or "General Project"
        }

        return True, "", sanitized_data