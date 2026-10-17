import sys
from src.storage import Storage
from src.request_handler import RequestHandler
from src.analytics import RequestAnalytics

def print_menu():
    print("\n==================================================")
    print("  SDLC AI AGENT - FEATURE REQUEST SYSTEM (v1.0)")
    print("==================================================")
    print("1. Add Request (Secure Agent + Artifact + Logging)")
    print("2. View Requests & Artifacts")
    print("3. View Analytics & Generate Chart")
    print("4. View Agent Short-Term Memory")
    print("5. View Monitoring Dashboard & Metrics")
    print("6. Help & Documentation")
    print("7. Exit")
    print("==================================================")

def display_help():
    print("\n==================================================")
    print("              SYSTEM DOCUMENTATION                ")
    print("==================================================")
    print("Overview:")
    print("  This system automates feature request processing, SDLC")
    print("  phase detection using LangChain & OpenAI, artifact document")
    print("  generation, and operational monitoring.")
    print("\nWorkflow Instructions:")
    print("  1. Select Option 1 to submit a feature request.")
    print("     - Description: 10 to 500 characters.")
    print("     - Rate limit: 1.5s cooldown between requests.")
    print("  2. The AI Agent automatically determines the SDLC phase:")
    print("     (requirements, design, implementation, testing, deployment)")
    print("  3. A professional markdown artifact is generated in '/artifacts'.")
    print("  4. View stored requests, analytics charts, and live metrics")
    print("     through options 2, 3, and 5.")
    print("==================================================")

def main():
    storage = Storage()
    handler = RequestHandler(storage)
    analytics = RequestAnalytics()

    while True:
        print_menu()
        choice = input("Select an option (1-7): ").strip()

        if choice == "1":
            print("\n--- Add New Feature Request ---")
            description = input("Enter request description (10-500 chars): ")
            client = input("Enter client name: ")
            project = input("Enter project name: ")

            success, message = handler.add_request(description, client, project)
            print(f"\n[{'SUCCESS' if success else 'ERROR'}]\n{message}")

        elif choice == "2":
            print("\n--- Stored Feature Requests & Generated Artifacts ---")
            requests = handler.get_all_requests()
            if not requests:
                print("No requests found.")
            else:
                for req in requests:
                    print(f"\nID: {req['id']}")
                    print(f"Project: {req['project']} | Client: {req['client']}")
                    print(f"Description: {req['description']}")
                    print(f"SDLC Phase: {req.get('phase', 'N/A').upper()} (Confidence: {req.get('confidence', 'N/A')})")
                    print(f"Artifact File: {req.get('artifact_path', 'None')}")
                    print(f"Timestamp: {req['timestamp']}")
                    print("-" * 30)

        elif choice == "3":
            print("\n--- Request Analytics & Insights ---")
            stats = analytics.get_summary_statistics()
            
            print(f"Total Requests: {stats['total_requests']}")
            print(f"Average Description Length: {stats['avg_length']} characters")
            print("\nKeyword Frequencies:")
            for kw, count in stats['keyword_counts'].items():
                print(f"  - '{kw}': {count}")

            chart_path = analytics.generate_chart()
            print(f"\n[SUCCESS] Bar chart successfully generated and saved to '{chart_path}'!")

        elif choice == "4":
            print("\n--- Agent Short-Term Memory Context ---")
            memory = handler.agent.get_memory_context()
            if not memory:
                print("Agent memory is currently empty.")
            else:
                for idx, item in enumerate(memory, 1):
                    print(f"\nInteraction #{idx}:")
                    print(f"  Project: {item['observation']['project']}")
                    print(f"  Request: {item['observation']['description']}")
                    print(f"  Detected Phase: {item['reasoning']['phase'].upper()}")
                    print(f"  Action Summary: {item['action_summary']}")
                    print("-" * 30)

        elif choice == "5":
            print("\n========================================")
            print("          MONITORING DASHBOARD          ")
            print("========================================")
            stats = handler.monitor.get_dashboard_stats()
            print(f"Total Interactions Processed: {stats['total_interactions']}")
            print(f"Success Rate: {stats['success_rate']}%")
            print(f"Average Response Time: {stats['avg_response_time']} seconds")
            
            print("\nDetected Phases Breakdown:")
            if not stats['phase_counts']:
                print("  No phase data recorded yet.")
            else:
                for phase, count in stats['phase_counts'].items():
                    print(f"  - {phase.upper()}: {count} time(s)")

            print("\nRecent Errors / Issues:")
            if not stats['recent_errors']:
                print("  None! System is running smoothly.")
            else:
                for err in stats['recent_errors']:
                    print(f"  ⚠️ {err}")
            print("========================================")

        elif choice == "6":
            display_help()

        elif choice == "7":
            print("\nExiting application. Goodbye!")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid choice. Please enter a number between 1 and 7.")

if __name__ == "__main__":
    main()