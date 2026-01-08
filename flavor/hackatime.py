# flavor/hackatime.py
import requests
from flavor.config import get_hackatime_key

HACKATIME_BASE_URL = "https://hackatime.hackclub.com"

class HackatimeAPIError(Exception):
    pass

def _get_headers():
    key = get_hackatime_key()
    if not key:
        raise HackatimeAPIError("No Hackatime key found. Please run 'flavor login-hackatime <key>' first.")
    return {
        "Authorization": f"Bearer {key}",
    }

def get_time_today():
    # GET /api/hackatime/v1/users/current/statusbar/today
    url = f"{HACKATIME_BASE_URL}/api/hackatime/v1/users/current/statusbar/today"
    try:
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 401:
             raise HackatimeAPIError("Invalid API key or unauthorized access.")
        raise HackatimeAPIError(f"Failed to fetch today's time: {str(e)}")

def get_stats(username: str):
    # GET /api/v1/users/{username}/stats
    url = f"{HACKATIME_BASE_URL}/api/v1/users/{username}/stats"
    try:
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 401:
             raise HackatimeAPIError("Invalid API key or unauthorized access.")
        raise HackatimeAPIError(f"Failed to fetch stats: {str(e)}")
