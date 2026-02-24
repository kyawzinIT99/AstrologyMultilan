import requests
import json

BASE_URL = "https://kyawzin-ccna--astrology-chatbot-mm-wsgi-app.modal.run"

s = requests.Session()
login_resp = s.post(f"{BASE_URL}/login", data={"username": "kyawzin", "password": "Kyawzin@123456"})
print("Modal Login Status:", login_resp.status_code)

pdf_resp = s.post(f"{BASE_URL}/api/admin/generate_pdf", json={"name": "Modal User", "dob": "1994-05-15", "is_wednesday_pm": False})
print("Modal PDF Gen Status:", pdf_resp.status_code)
try:
    print("Modal PDF Gen Response:", pdf_resp.json())
except Exception as e:
    print("Modal PDF Error:", pdf_resp.text)
