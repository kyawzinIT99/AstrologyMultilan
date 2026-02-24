import requests

s = requests.Session()
# Login
resp = s.post("http://localhost:5050/login", data={"username": "kyawzin", "password": "Kyawzin@123456"})
print("Login Status:", resp.status_code)

# Generate PDF
resp = s.post("http://localhost:5050/api/admin/generate_pdf", json={"name": "Kyaw Zin", "dob": "1994-05-15", "is_wednesday_pm": False})
print("PDF Generation Response:", resp.json())
