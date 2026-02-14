#!/usr/bin/env python3
"""
Simple server script to generate notes.json and serve git commits API.
Run on your server to manage notes locally.
"""

import json
import os
import subprocess
import re
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import time

NOTES_DIR = "./notes"
NOTES_JSON = "./notes.json"
GIT_DIR = "."


def parse_note_metadata(filepath):
    """Parse metadata from HTML comment in note file."""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        # Find metadata comment
        meta_match = re.search(r"<!--\s*([\s\S]*?)\s*-->", content)
        metadata = {}

        if meta_match:
            meta_text = meta_match[1]
            for line in meta_text.split("\n"):
                match = re.match(r"^\s*(\w+):\s*(.+)$", line)
                if match:
                    key, value = match.groups()
                    metadata[key] = value.strip()

        # Get git commit date
        git_date = get_git_date(filepath)

        filename = os.path.basename(filepath)
        slug = filename.replace(".html", "")

        return {
            "slug": slug,
            "date": metadata.get("date", git_date),
            "title": metadata.get("title", slug),
            "title_ru": metadata.get("title_ru", metadata.get("title", slug)),
            "description": metadata.get("description", ""),
            "description_ru": metadata.get("description_ru", ""),
            "tags": [
                t.strip() for t in metadata.get("tags", "").split(",") if t.strip()
            ],
            "status": metadata.get("status", "published"),
            "draft": metadata.get("draft", "").lower() == "true",
            "url": f"/notes/{filename}",
        }
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
        return None


def get_git_date(filepath):
    """Get last commit date for file."""
    try:
        result = subprocess.run(
            ["git", "log", "-1", "--format=%ci", filepath],
            capture_output=True,
            text=True,
            cwd=GIT_DIR,
        )
        if result.returncode == 0:
            date_str = result.stdout.strip().split()[0]
            return date_str
    except:
        pass
    return datetime.now().strftime("%Y-%m-%d")


def get_git_commits(limit=10):
    """Get recent git commits."""
    try:
        result = subprocess.run(
            ["git", "log", f"--max-count={limit}", "--format=%H|%ci|%s"],
            capture_output=True,
            text=True,
            cwd=GIT_DIR,
        )
        if result.returncode == 0:
            commits = []
            for line in result.stdout.strip().split("\n"):
                if "|" in line:
                    parts = line.split("|", 2)
                    if len(parts) == 3:
                        hash_full, date_str, message = parts
                        commits.append(
                            {
                                "hash": hash_full[:7],
                                "date": date_str.split()[0],
                                "message": message,
                            }
                        )
            return commits
    except Exception as e:
        print(f"Error getting commits: {e}")
    return []


def generate_notes_json():
    """Generate notes.json from all note files."""
    if not os.path.exists(NOTES_DIR):
        return

    notes = []
    for filename in sorted(os.listdir(NOTES_DIR)):
        if filename.endswith(".html"):
            filepath = os.path.join(NOTES_DIR, filename)
            note = parse_note_metadata(filepath)
            if note and not note["draft"] and note["status"] == "published":
                notes.append(note)

    # Sort by date descending
    notes.sort(key=lambda x: x["date"], reverse=True)

    data = {"updated": datetime.now().isoformat(), "count": len(notes), "notes": notes}

    with open(NOTES_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Generated {NOTES_JSON} with {len(notes)} notes")


class APIHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/api/commits":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            commits = get_git_commits(10)
            self.wfile.write(json.dumps(commits).encode())
        elif self.path == "/api/rebuild":
            # Trigger notes.json rebuild
            generate_notes_json()
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"status": "ok"}).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        # Suppress logs
        pass


def watch_and_rebuild():
    """Watch for changes and rebuild notes.json."""
    last_mtime = 0
    while True:
        try:
            current_mtime = 0
            if os.path.exists(NOTES_DIR):
                for root, dirs, files in os.walk(NOTES_DIR):
                    for f in files:
                        if f.endswith(".html"):
                            filepath = os.path.join(root, f)
                            try:
                                current_mtime = max(
                                    current_mtime, os.path.getmtime(filepath)
                                )
                            except:
                                pass

            if current_mtime > last_mtime:
                generate_notes_json()
                last_mtime = current_mtime
        except Exception as e:
            print(f"Watch error: {e}")

        time.sleep(5)


def main():
    # Initial build
    generate_notes_json()

    # Start watcher thread
    watcher = threading.Thread(target=watch_and_rebuild, daemon=True)
    watcher.start()

    # Start API server
    server = HTTPServer(("127.0.0.1", 8081), APIHandler)
    print("API server running on http://127.0.0.1:8081")
    print("Endpoints:")
    print("  GET /api/commits - get recent git commits")
    print("  GET /api/rebuild - force rebuild notes.json")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")


if __name__ == "__main__":
    main()
