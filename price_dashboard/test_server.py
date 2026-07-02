import requests

r = requests.get('http://localhost:8506/dashboard.html')
print(f"Status: {r.status_code}")
print(f"Content length: {len(r.text)}")
print(f"First 200 chars: {r.text[:200]}")