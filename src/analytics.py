import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Dict, Any

class RequestAnalytics:
    def __init__(self, data_filepath: str = "data/requests.json"):
        self.data_filepath = data_filepath

    def _load_dataframe(self) -> pd.DataFrame:
        """Load requests JSON into a pandas DataFrame."""
        if not os.path.exists(self.data_filepath):
            return pd.DataFrame(columns=["id", "description", "client", "project", "timestamp"])
        
        try:
            df = pd.read_json(self.data_filepath)
            if df.empty:
                return pd.DataFrame(columns=["id", "description", "client", "project", "timestamp"])
            return df
        except Exception:
            return pd.DataFrame(columns=["id", "description", "client", "project", "timestamp"])

    def get_summary_statistics(self) -> Dict[str, Any]:
        """Calculate total requests and average description length."""
        df = self._load_dataframe()
        if df.empty:
            return {
                "total_requests": 0,
                "avg_length": 0.0,
                "keyword_counts": {}
            }

        total_requests = len(df)
        
        # Calculate average character length of descriptions
        df['length'] = df['description'].astype(str).str.len()
        avg_length = float(df['length'].mean())

        # Simple keyword frequency analysis
        keywords = ["login", "database", "test", "system", "user", "payment", "add", "create"]
        keyword_counts = {}
        
        all_text = " ".join(df['description'].astype(str).str.lower())
        for kw in keywords:
            keyword_counts[kw] = all_text.count(kw)

        return {
            "total_requests": total_requests,
            "avg_length": round(avg_length, 2),
            "keyword_counts": keyword_counts
        }

    def generate_chart(self, output_path: str = "data/request_chart.png") -> str:
        """Generate a basic bar chart of keyword frequencies and save as PNG."""
        stats = self.get_summary_statistics()
        keyword_counts = stats["keyword_counts"]

        # Ensure data folder exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        # Plotting with matplotlib
        plt.figure(figsize=(8, 5))
        keywords = list(keyword_counts.keys())
        counts = list(keyword_counts.values())

        plt.bar(keywords, counts, color='skyblue', edgecolor='black')
        plt.xlabel("Keywords")
        plt.ylabel("Frequency")
        plt.title("Feature Request Keyword Frequencies")
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Save chart
        plt.savefig(output_path)
        plt.close()

        return output_path