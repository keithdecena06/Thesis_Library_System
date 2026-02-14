#!/usr/bin/env python
"""
Test script for RFID API
"""
import urllib.request
import json

# Test the RFID API
url = "http://127.0.0.1:8000/api/rfid_log/"
rfid_url = "http://127.0.0.1:8000/api/rfid/"
# Test home page first
home_url = "http://127.0.0.1:8000/"

try:
    with urllib.request.urlopen(home_url) as response:
        print(f"Home page works: {response.getcode()}")
except Exception as e:
    print(f"Home page error: {e}")

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/rfid_log/") as response:
        print(f"GET /api/rfid_log/ works: {response.getcode()}")
except Exception as e:
    print(f"GET /api/rfid_log/ error: {e}")

try:
    with urllib.request.urlopen("http://127.0.0.1:8000/api/rfid_log") as response:
        print(f"GET /api/rfid_log works: {response.getcode()}")
except Exception as e:
    print(f"GET /api/rfid_log error: {e}")

data = {"uid": "0B506E05"}
data_json = json.dumps(data).encode('utf-8')

print(f"Testing {url}")
try:
    req = urllib.request.Request(url, data=data_json, headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(req) as response:
        print(f"Status Code: {response.getcode()}")
        response_data = json.loads(response.read().decode('utf-8'))
        print(f"Response: {response_data}")
except urllib.error.HTTPError as e:
    print(f"HTTP Error: {e.code}")
    print(f"Response: {e.read().decode('utf-8')}")
except Exception as e:
    print(f"Error: {e}")