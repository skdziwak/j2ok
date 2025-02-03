import argparse
import requests
import sys
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser(description="Fetch 'Assigned to me' Jira tickets and update an Obsidian MD kanban board")
    parser.add_argument('--jira-url', required=True, help="Base URL for Jira, e.g., https://yourcompany.atlassian.net")
    parser.add_argument('--api-token', required=True, help="Jira API token or password")
    parser.add_argument('--outfile', required=True, help="Output markdown file path to overwrite")
    args = parser.parse_args()
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
        key = issue["key"]
        summary = issue["fields"]["summary"]

        board_columns[status].append(f"- [{key}] {summary}")

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
