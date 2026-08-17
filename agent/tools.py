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
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    resp = requests.get(url, headers=_headers())
    resp.raise_for_status()
    data = resp.json()
    return base64.b64decode(data["content"]).decode("utf-8", errors="replace")