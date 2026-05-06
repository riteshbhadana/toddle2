import os
import re
import requests
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("SERPAPI_KEY")


def find_linkedin(name, school):
    name = str(name).strip()
    school = str(school).split(";")[0].strip()

    query = f'"{name}" "{school}" site:linkedin.com/in'
    url = "https://serpapi.com/search"
    params = {
        "engine": "google",
        "q": query,
        "api_key": API_KEY,
        "num": 5,
    }

    try:
        res = requests.get(url, params=params, timeout=15)
        if res.status_code != 200:
            print(f"SerpAPI HTTP error: {res.status_code}")
            return fallback()

        data = res.json()

        for r in data.get("organic_results", []):
            link = r.get("link", "")
            if "linkedin.com/in/" not in link:
                continue

            # ── Try to extract current school from the snippet ──
            snippet = r.get("snippet", "")
            title   = r.get("title", "")
            current_school = extract_school_from_text(snippet + " " + title)

            return {
                "linkedin": link,
                "current_school": current_school or "Unknown",
            }

    except requests.exceptions.Timeout:
        print("SerpAPI timeout")
    except Exception as e:
        print(f"SerpAPI error: {e}")

    return fallback()


# ── Heuristics to pull org/school name out of a LinkedIn snippet ──────────────
_AT_PATTERN   = re.compile(r'\bat\s+([A-Z][^·|•\n,]{2,50})', re.IGNORECASE)
_CURR_PATTERN = re.compile(
    r'(?:Current|Present|Now)[^\w]*[:\-–]?\s*([A-Z][^·|•\n,]{2,50})',
    re.IGNORECASE,
)
_DASH_PATTERN = re.compile(r'-\s*([A-Z][^·|•\n,]{2,50})', re.IGNORECASE)


def extract_school_from_text(text: str) -> str:
    """
    Tries several regex patterns to pull the current organisation
    from a LinkedIn Google snippet.  Returns empty string if nothing found.
    """
    for pattern in (_CURR_PATTERN, _AT_PATTERN, _DASH_PATTERN):
        m = pattern.search(text)
        if m:
            candidate = m.group(1).strip().rstrip(".")
            # Filter out noise like "LinkedIn", "View", etc.
            noise = {"linkedin", "view", "profile", "connect", "see", "more"}
            if candidate.lower().split()[0] not in noise:
                return candidate
    return ""


def fallback():
    return {
        "linkedin": "Not Found",
        "current_school": "Unknown",
    }
