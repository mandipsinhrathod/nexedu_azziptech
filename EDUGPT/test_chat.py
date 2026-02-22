import requests
import json

url = "http://127.0.0.1:5000/api/chat"
headers = {"Content-Type": "application/json"}

messages = [
    "Hello",
    "no",
    "roadmap to python",
    "why is this completely broken",
    "ok"
]

print("--- Testing Chat API ---")
for msg in messages:
    print(f"\nUser: {msg}")
    try:
        data = {"message": msg, "agent": "The Architect"}
        response = requests.post(url, json=data)
        if response.status_code == 200:
            print(f"Bot:  {response.json().get('reply')}")
        else:
            print(f"Error {response.status_code}: {response.text}")
    except Exception as e:
        print(f"Connection Failed: {e}")
