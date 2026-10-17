import sys
from src.storage import Storage
from src.request_handler import RequestHandler
from src.analytics import RequestAnalytics

def print_menu():
    print("\n========================================")
    print("  FEATURE REQUEST MANAGEMENT & ANALYTICS")
    print("========================================")
    print("1. Add Request")
    print("2. View Requests")
    print("3. View Analytics & Generate Chart")
    print("4. View Agent Memory (Last 2 Interactions)")
    print("5. Exit")
    print("========================================")

def main():
    storage = Storage()
    handler = RequestHandler(storage)
    analytics = RequestAnalytics()

    while True:
        print_menu()
        choice = input("Select an option (1-5): ").strip()

        if choice == "1":
            print("\n--- Add New Feature Request ---")
            description = input("Enter request description (10-500 chars): ")
            client = input("Enter client name: ")
            project = input("Enter project name: ")

            success, message = handler.add_request(description, client, project)
            print(f"\n[{'SUCCESS' if success else 'ERROR'}] {message}")

        # elif choice == "2":
        #     print("\n--- Stored Feature Requests ---")
        #     requests = handler.get_all_requests()
        #     if not requests:
        #         print("No requests found.")
        #     else:
        #         for req in requests:
        #             print(f"\nID: {req['id']}")
        #             print(f"Project: {req['project']} | Client: {req['client']}")
        #             print(f"Description: {req['description']}")
        #             print(f"Timestamp: {req['timestamp']}")
        #             print("-" * 30)

        # elif choice == "2":
        #     print("\n--- Stored Feature Requests & AI Phases ---")
        #     requests = handler.get_all_requests()
        #     if not requests:
        #         print("No requests found.")
        #     else:
        #         for req in requests:
        #             print(f"\nID: {req['id']}")
        #             print(f"Project: {req['project']} | Client: {req['client']}")
        #             print(f"Description: {req['description']}")
        #             print(f"SDLC Phase: {req.get('phase', 'N/A')} (Confidence: {req.get('confidence', 'N/A')})")
        #             print(f"Timestamp: {req['timestamp']}")
        #             print("-" * 30)

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

            # Generate chart
            chart_path = analytics.generate_chart()
            print(f"\n[SUCCESS] Bar chart successfully generated and saved to '{chart_path}'!")

        # elif choice == "4":
        #     print("\nExiting application. Goodbye!")
        #     sys.exit(0)

        elif choice == "4":
            print("\n--- Agent Short-Term Memory Context ---")
            memory = handler.agent.get_memory_context()
            if not memory:
                print("Agent memory is currently empty (no interactions processed yet in this session).")
            else:
                for idx, item in enumerate(memory, 1):
                    print(f"\nInteraction #{idx}:")
                    print(f"  Project: {item['observation']['project']}")
                    print(f"  Request: {item['observation']['description']}")
                    print(f"  Detected Phase: {item['reasoning']['phase'].upper()}")
                    print(f"  Action Summary: {item['action_summary']}")
                    print("-" * 30)
        elif choice == "5":
            print("\nExiting application. Goodbye!")
            sys.exit(0)
        else:
            print("\n[ERROR] Invalid choice. Please enter a number between 1 and 4.")

if __name__ == "__main__":
    main()