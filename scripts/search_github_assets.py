import urllib.request
import json
import re

headers = {"User-Agent": "Mozilla/5.0"}

def search_repo_images(repo_name):
    # Get tree of repo
    url = f"https://api.github.com/repos/{repo_name}/git/trees/main?recursive=1"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            tree = json.loads(r.read().decode()).get("tree", [])
            imgs = [f["path"] for f in tree if f["path"].lower().endswith((".jpg", ".png", ".webp")) and any(k in f["path"].lower() for k in ["cable", "clip", "photo", "img", "doc"])]
            return imgs
    except Exception:
        # try master
        try:
            url = f"https://api.github.com/repos/{repo_name}/git/trees/master?recursive=1"
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=5) as r:
                tree = json.loads(r.read().decode()).get("tree", [])
                imgs = [f["path"] for f in tree if f["path"].lower().endswith((".jpg", ".png", ".webp")) and any(k in f["path"].lower() for k in ["cable", "clip", "photo", "img", "doc"])]
                return imgs
        except Exception:
            return []

# Search Voron or 3d print cable management repos
url = "https://api.github.com/search/repositories?q=cable+management+3d+print&sort=stars"
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=8) as r:
        repos = json.loads(r.read().decode()).get("items", [])
        for repo in repos[:8]:
            name = repo["full_name"]
            imgs = search_repo_images(name)
            if imgs:
                print(f"Repo {name}:")
                for img in imgs[:5]:
                    raw_url = f"https://raw.githubusercontent.com/{name}/HEAD/{img}"
                    print(f"  {raw_url}")
except Exception as e:
    print("Error:", e)
