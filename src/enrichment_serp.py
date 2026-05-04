import os
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SERPAPI_KEY")


def find_linkedin(name, school):
    name = str(name).strip()
    school = str(school).split(";")[0].strip()

    # बेहतर matching के लिए quotes + site filter
    query = f'"{name}" "{school}" site:linkedin.com/in'

    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY
    }

    try:
        res = requests.get(url, params=params, timeout=10)
        if res.status_code != 200:
            return fallback()

        data = res.json()

        for r in data.get("organic_results", []):
            link = r.get("link", "")
            if "linkedin.com/in/" in link:
                # अभी enrichment नहीं है, इसलिए new school unknown
                return {
                    "linkedin": link,
                    "current_school": "Unknown"
                }

    except Exception as e:
        print("SerpAPI error:", e)

    return fallback()


def fallback():
    return {
        "linkedin": "Not Found",
        "current_school": "Unknown"
    }