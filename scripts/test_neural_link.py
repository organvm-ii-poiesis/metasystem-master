#!/usr/bin/env python3
import requests
import hmac
import hashlib
import json
import time

URL = "http://localhost:3000/api/webhooks/github"
SECRET = "development-secret" # allow-secret

def sign_payload(payload):
    body = json.dumps(payload) # Note: Whitespace matching is tricky with JSON.stringify vs json.dumps
    # In Node: JSON.stringify({"foo":"bar"}) -> '{"foo":"bar"}'
    # In Python: json.dumps({"foo":"bar"}) -> '{"foo": "bar"}' (default has spaces)
    # We need to use separators to match Node's default or just rely on body parser behaving.
    # Let's try default python dumps and see if express receives it.
    
    # Actually, the best way is to send raw bytes and sign them.
    return hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()

def test_webhook():
    payload = {
        "ref": "refs/heads/main",
        "repository": {
            "full_name": "omni-dromenon-machina/core-engine",
            "html_url": "https://github.com/..."
        },
        "sender": {
            "login": "4444JPP"
        }
    }
    
    body = json.dumps(payload)
    signature = "sha256=" + hmac.new(SECRET.encode(), body.encode(), hashlib.sha256).hexdigest()
    
    headers = {
        "Content-Type": "application/json",
        "X-Hub-Signature-256": signature,
        "X-GitHub-Event": "push"
    }
    
    print(f"⚡ Firing Neuron at {URL}...")
    try:
        res = requests.post(URL, data=body, headers=headers, timeout=2)
        print(f"   Status: {res.status_code}")
        print(f"   Response: {res.text}")
        
        if res.status_code == 200:
            print("✅ Neural Link Active.")
        else:
            print("❌ Neural Link Broken.")
            
    except Exception as e:
        print(f"❌ Connection Failed: {e}")
        print("   (Is the core-engine running?)")

if __name__ == "__main__":
    test_webhook()
