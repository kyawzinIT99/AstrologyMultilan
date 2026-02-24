import requests

BASE_URL = "https://kyawzin-ccna--astrology-chatbot-mm-wsgi-app.modal.run"
s = requests.Session()
s.post(f"{BASE_URL}/login", data={"username": "kyawzin", "password": "Kyawzin@123456"})

# Simulate what the frontend does: BE 2531 - 543 = 1988 CE
be_year = 2531
ce_year = be_year - 543  # = 1988
dob = f"{ce_year}-05-15"  # 1988-05-15

resp = s.post(f"{BASE_URL}/api/admin/generate_pdf", json={
    "name": "BE Test User",
    "dob": dob,
    "is_wednesday_pm": False
})
print(f"BE 2531 → CE {ce_year} → dob={dob}")
print("Status:", resp.status_code)
print("Response:", resp.json())
