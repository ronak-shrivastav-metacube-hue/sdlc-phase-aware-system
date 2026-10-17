import time
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, Tuple
from src.storage import Storage
from src.langchain_agent import LangChainAgent
from src.artifact_generator import ArtifactGenerator
from src.monitoring import AgentMonitor
from src.security import SecurityGuard

@dataclass
class FeatureRequest:
    id: str
    description: str
    client: str
    project: str
    timestamp: str
    phase: str
    confidence: str
    artifact_path: str

class RequestHandler:
    def __init__(self, storage: Storage):
        self.storage = storage
        self.agent = LangChainAgent()
        self.artifact_generator = ArtifactGenerator()
        self.monitor = AgentMonitor()
        self.security = SecurityGuard(rate_limit_seconds=1.5)  # Initialize Security Guard

    def add_request(self, description: str, client: str, project: str) -> Tuple[bool, str]:
        """Validate, sanitize, time execution, run agent, log metrics, and persist request."""
        
        # 1. Security Validation & Sanitization
        is_valid, err_msg, clean_data = self.security.validate_and_sanitize(description, client, project)
        if not is_valid:
            self.monitor.log_interaction(project=project or "Unknown", phase="none", response_time=0.0, success=False, error_msg=err_msg)
            return False, err_msg

        print("\n🛡️ [Security Verified] Input sanitized & validated. Processing request...")
        start_time = time.time()
        
        try:
            # 2. Run LangChain Agent
            agent_result = self.agent.process_request(
                description=clean_data["description"],
                client=clean_data["client"],
                project=clean_data["project"]
            )
            detected_phase = agent_result["phase"]

            # 3. Generate artifact
            artifact_path = self.artifact_generator.generate_artifact(
                phase=detected_phase,
                description=clean_data["description"],
                project=clean_data["project"],
                client=clean_data["client"]
            )

            response_time = time.time() - start_time

            # Log success metrics
            self.monitor.log_interaction(
                project=clean_data["project"],
                phase=detected_phase,
                response_time=response_time,
                success=True
            )

            existing_requests = self.storage.load_data()
            new_id = str(len(existing_requests) + 1)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            req = FeatureRequest(
                id=new_id,
                description=clean_data["description"],
                client=clean_data["client"],
                project=clean_data["project"],
                timestamp=timestamp,
                phase=detected_phase,
                confidence=agent_result["confidence"],
                artifact_path=artifact_path
            )

            self.storage.append_record(asdict(req))
            
            summary_msg = (
                f"Successfully created request #{new_id} (Processed in {response_time:.2f}s)!\n"
                f"   ↳ {agent_result['summary']}\n"
                f"   📄 Artifact Document Saved: `{artifact_path}`"
            )
            return True, summary_msg

        except Exception as e:
            response_time = time.time() - start_time
            error_str = str(e)
            
            # Log failure metrics
            self.monitor.log_interaction(
                project=clean_data.get("project", "Unknown"),
                phase="error",
                response_time=response_time,
                success=False,
                error_msg=error_str
            )
            return False, f"Error processing request: {error_str}"

    def get_all_requests(self) -> list:
        return self.storage.load_data()