import os
import time
import json
from datetime import datetime
from typing import Dict, Any, List

class AgentMonitor:
    def __init__(self, log_filepath: str = "data/agent_logs.log", metrics_filepath: str = "data/metrics.json"):
        self.log_filepath = log_filepath
        self.metrics_filepath = metrics_filepath
        self._ensure_files_exist()

    def _ensure_files_exist(self) -> None:
        """Ensure log files and metrics storage exist."""
        os.makedirs(os.path.dirname(self.log_filepath), exist_ok=True)
        if not os.path.exists(self.log_filepath):
            with open(self.log_filepath, "w", encoding="utf-8") as f:
                f.write("--- Agent Execution Logs ---\n")
        
        if not os.path.exists(self.metrics_filepath):
            self._save_metrics({
                "total_interactions": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "phase_counts": {},
                "total_response_time": 0.0,
                "recent_errors": []
            })

    def _load_metrics(self) -> Dict[str, Any]:
        """Load current metrics from JSON file."""
        try:
            with open(self.metrics_filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {
                "total_interactions": 0,
                "successful_interactions": 0,
                "failed_interactions": 0,
                "phase_counts": {},
                "total_response_time": 0.0,
                "recent_errors": []
            }

    def _save_metrics(self, metrics: Dict[str, Any]) -> None:
        """Save metrics to JSON file."""
        with open(self.metrics_filepath, "w", encoding="utf-8") as f:
            json.dump(metrics, f, indent=4)

    def log_interaction(self, project: str, phase: str, response_time: float, success: bool, error_msg: str = None) -> None:
        """Log an interaction, update performance metrics, and append to log file."""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = "SUCCESS" if success else "FAILED"
        
        # 1. Write to text log file
        log_entry = f"[{timestamp}] [{status}] Project: {project} | Phase: {phase} | Time: {response_time:.2f}s"
        if error_msg:
            log_entry += f" | Error: {error_msg}"
        
        with open(self.log_filepath, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

        # 2. Update persistent metrics
        metrics = self._load_metrics()
        metrics["total_interactions"] += 1
        metrics["total_response_time"] += response_time

        if success:
            metrics["successful_interactions"] += 1
            # Track phase counts
            phase_lower = phase.lower()
            metrics["phase_counts"][phase_lower] = metrics["phase_counts"].get(phase_lower, 0) + 1
        else:
            metrics["failed_interactions"] += 1
            if error_msg:
                metrics["recent_errors"].append(f"[{timestamp}] {error_msg}")
                # Keep only last 5 recent errors
                if len(metrics["recent_errors"]) > 5:
                    metrics["recent_errors"].pop(0)

        self._save_metrics(metrics)

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Calculate and return summarized metrics for the monitoring dashboard."""
        metrics = self._load_metrics()
        total = metrics["total_interactions"]
        
        if total == 0:
            success_rate = 100.0
            avg_response_time = 0.0
        else:
            success_rate = (metrics["successful_interactions"] / total) * 100
            avg_response_time = metrics["total_response_time"] / total

        return {
            "total_interactions": total,
            "success_rate": round(success_rate, 2),
            "avg_response_time": round(avg_response_time, 2),
            "phase_counts": metrics["phase_counts"],
            "recent_errors": metrics["recent_errors"]
        }