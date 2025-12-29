#!/usr/bin/env python3
import os
import json
import sys
import urllib.request
from pathlib import Path

# --- Configuration ---
WORKSPACE_ROOT = Path("/Users/4jp/Workspace")
INDEX_FILE = WORKSPACE_ROOT / "omni-dromenon-machina/data/universe_index.json"
GEMINI_KEY = os.environ.get("GEMINI_API_KEY")

if not GEMINI_KEY:
    print("❌ Error: GEMINI_API_KEY is not set.")
    sys.exit(1)

def load_index():
    if not INDEX_FILE.exists():
        print(f"❌ Error: Index not found at {INDEX_FILE}")
        sys.exit(1)
    with open(INDEX_FILE, 'r') as f:
        return json.load(f)

def retrieve_context(query, index, limit=5):
    query_terms = set(query.lower().split())
    scored = []
    for entry in index:
        score = 0
        text_blob = f"{entry['repo']} {entry['name']} ".lower()
        for f in entry['files']:
            text_blob += f['content'].lower()
        for term in query_terms:
            if term in text_blob:
                score += 1
        if score > 0:
            scored.append((score, entry))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [x[1] for x in scored[:limit]]

def ask_gemini(query, context_entries):
    context_str = ""
    for entry in context_entries:
        context_str += f"--- REPO: {entry['repo']} ---\n"
        for f in entry['files']:
            context_str += f"FILE: {f['name']}\n{f['content'][:1500]}\n"
        context_str += "\n"

    system_prompt = "You are the Architect of the Omni-Dromenon Metasystem. Use the provided context to answer questions about the codebase history."
    user_message = f"CONTEXT:\n{context_str}\n\nQUESTION: {query}"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={GEMINI_KEY}"
    
    data = {
        "contents": [{
            "parts": [{"text": f"SYSTEM: {system_prompt}\n\nUSER: {user_message}"}]
        }]
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers={'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        return f"❌ API Error: {e}"

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 scripts/ask_origin.py \"Your question here\"")
        sys.exit(1)

    query = sys.argv[1]
    print(f"🔍 Searching Memory for: '{query}'...")
    index = load_index()
    results = retrieve_context(query, index)
    
    if not results:
        print("   ⚠️  No relevant repositories found.")
        return

    print(f"   📚 Context found in {len(results)} repositories.")
    print("\n💬 The Architect Says:")
    print("---------------------------------------------------")
    print(ask_gemini(query, results))
    print("---------------------------------------------------")

if __name__ == "__main__":
    main()