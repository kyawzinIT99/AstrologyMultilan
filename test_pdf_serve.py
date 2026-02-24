import requests

BASE_URL = "https://kyawzin-ccna--astrology-chatbot-mm-wsgi-app.modal.run"
s = requests.Session()
s.post(f"{BASE_URL}/login", data={"username": "kyawzin", "password": "Kyawzin@123456"})

gen_resp = s.post(f"{BASE_URL}/api/admin/generate_pdf", json={"name": "Log Test", "dob": "1994-05-15", "is_wednesday_pm": False})
data = gen_resp.json()
print("Gen Status:", gen_resp.status_code)
print("Gen Response:", data)

if "url" in data:
    pdf_url = BASE_URL + data["url"]
    print(f"Fetching PDF from: {pdf_url}")
    pdf_resp = s.get(pdf_url)
    print("PDF Status:", pdf_resp.status_code)
    print("PDF Headers:", pdf_resp.headers)
    print("PDF Content Length:", len(pdf_resp.content))
    if len(pdf_resp.content) > 0:
        print("First 20 bytes of content:", pdf_resp.content[:20])
