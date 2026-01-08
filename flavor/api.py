import requests
from flavor.config import get_api_key

API_BASE_URL = "https://flavortown.hackclub.com"

class APIError(Exception):
    pass

def _get_headers():
    key = get_api_key()
    if not key:
        raise APIError("Not logged in. Please run 'flavor login <api_key>' first.")
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json"
    }

def get_users():
    url = f"{API_BASE_URL}/api/v1/users"
    try:
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 401:
             raise APIError("Invalid API key or unauthorized access.")
        raise APIError(f"Failed to fetch users: {str(e)}")
