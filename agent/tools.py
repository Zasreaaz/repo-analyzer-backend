import base64
import os 
import requests

GITHUB_API_URL = "https://api.github.com"

def _headers():
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers

def list_repo_files(owner: str, repo: str, path: str = "") -> str:
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()
    items = resp.json()
    if isinstance(items, dict):
        return [items["path"]]
    return "\n".join(f"{item['type']}: {item['path']}" for item in items)
    
def read_repo_file(owner: str, repo: str, path: str) -> str:
    url = f"{GITHUB_API_URL}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")

TOOLS = [
    {
        "name": "list_repo_files",
        "description": (
            "List files and directories at a given path in the GitHub repository. "
            "Call with path='' to list the repo root. Use this to explore the project "
            "structure before reading specific files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "path": {"type": "string", "description": "Empty string for repo root"},
            },
            "required": ["owner", "repo"],
        },
    },
    {
        "name": "read_repo_file",
        "description": (
            "Read the full text content of a single file in the GitHub repository. "
            "Use this after list_repo_files to inspect specific source files, README, "
            "or config files."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "owner": {"type": "string"},
                "repo": {"type": "string"},
                "path": {"type": "string", "description": "e.g. src/main/App.java"},
            },
            "required": ["owner", "repo", "path"],
        },
    },
]

def execute_tool(name: str, tool_input: dict) -> str:
    try:
        if name == "list_repo_files":
            return list_repo_files(**tool_input)
        if name == "read_repo_file":
            return read_repo_file(**tool_input)
        return f"Unknown tool: {name}"
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else "?"
        return f"Error calling {name}: GitHub API returned {status} for {tool_input}"
    except requests.exceptions.RequestException as e:
        return f"Error calling {name}: {e}"