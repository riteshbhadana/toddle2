import os
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("PROXYCURL_API_KEY")

url = "https://nubela.co/proxycurl/api/v2/linkedin/profile/resolve"

headers = {
    "Authorization": f"Bearer {API_KEY}"
}

params = {
    "full_name": "Satya Nadella",
    "company_name": "Microsoft"
}

res = requests.get(url, headers=headers, params=params)

print("STATUS:", res.status_code)
print("RESPONSE:", res.text)