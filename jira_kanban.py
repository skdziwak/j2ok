import argparse
import requests
import sys
import os
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description="Fetch 'Assigned to me' Jira tickets and update an Obsidian MD kanban board")
    parser.add_argument('--jira-url', required=True, help="Base URL for Jira, e.g., https://yourcompany.atlassian.net")
    parser.add_argument('--api-token', required=True, help="Jira API token or password")
    parser.add_argument('--outfile', required=True, help="Output markdown file path to overwrite")
    parser.add_argument('--tickets-dir', default='tickets', help="Directory where each ticket MD file will be created")
    args = parser.parse_args()
    tickets_dir = args.tickets_dir
    os.makedirs(tickets_dir, exist_ok=True)
    
    # Clear tickets directory before regeneration
    import os  # already imported at top, so this is safe to reuse os module
    for file in os.listdir(tickets_dir):
        file_path = os.path.join(tickets_dir, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
    
    token = args.api_token

    search_url = f"{args.jira_url}/rest/api/2/search"
    # Query for issues assigned to the current user
    query = {
        "jql": "assignee=currentUser() and status != Done",
        "maxResults": 100
    }

    response = requests.get(search_url, params=query, headers={
        "Authorization": f"Bearer {token}",
        "Accept": "application/json"
        })
    if response.status_code != 200:
        print("Error accessing Jira API:", response.status_code, response.text)
        sys.exit(1)
    data = response.json()
    issues = data.get("issues", [])

    # Map issues to board columns based on status
    board_columns = defaultdict(list)

    for issue in issues:
        status = issue["fields"]["status"]["name"]
        if status == "Rejected":
            continue
        key = issue["key"]
        summary = issue["fields"]["summary"]

        ticket_detail_url = f"{args.jira_url}/rest/api/2/issue/{key}"
        detail_response = requests.get(ticket_detail_url, headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
            })
        if detail_response.status_code == 200:
            ticket_data = detail_response.json()
            description = ticket_data["fields"].get("description", "No details available.")
        else:
            description = "Error fetching details."
        
        ticket_path = os.path.join(tickets_dir, f"{key}.md")
        with open(ticket_path, "w") as t:
            t.write(f"# {key}\n\n**Summary:** {summary}\n\n**Details:**\n{description}")

        board_columns[status].append(f"- [[{tickets_dir}/{key}|{summary}]]")

    # Build the kanban board markdown content
    lines = []
    lines.append("---")
    lines.append("kanban-plugin: board")
    lines.append("---\n")
    for column in board_columns.keys():
        lines.append(f"## {column}\n")
        if board_columns[column]:
            lines.extend(board_columns[column])
        lines.append("\n")
    content = "\n".join(lines)

    # Overwrite the output file with the generated content
    with open(args.outfile, "w") as f:
        f.write(content)
    print(f"Kanban board updated in {args.outfile}")

if __name__ == "__main__":
    main()
