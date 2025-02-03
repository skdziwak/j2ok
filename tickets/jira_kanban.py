import requests

def fetch_ticket_description(ticket_id):
    # TODO: Replace with actual JIRA API endpoint and authentication details
    url = f"https://jira.example.com/rest/api/2/issue/{ticket_id}"
    response = requests.get(url)
    if response.status_code == 200:
        issue = response.json()
        return issue.get("fields", {}).get("description", "")
    else:
        return ""

def write_ticket_description(ticket_id, description):
    with open(f"tickets/{ticket_id}.txt", "w") as f:
        f.write(description)

def main():
    # List of ticket IDs to process. Replace with actual ticket IDs or logic as needed.
    ticket_ids = ["TICKET-1", "TICKET-2"]
    for ticket_id in ticket_ids:
        description = fetch_ticket_description(ticket_id)
        write_ticket_description(ticket_id, description)
        print(f"Ticket {ticket_id} description written to tickets/{ticket_id}.txt")

if __name__ == "__main__":
    main()
