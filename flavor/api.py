import requests
from flavor.config import get_api_key

API_BASE_URL = "https://flavortown.hackclub.com"

class APIError(Exception):
    pass

def _get_headers():
    key = get_api_key()
    if not key:
        raise APIError("Not logged in. Please run 'flavor login <api_key>' first.")
    
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "X-Flavortown-Ext-5800": "true"
    }

    return headers

def get_users(page: int = 1, query: str = None):
    url = f"{API_BASE_URL}/api/v1/users"
    params = {"page": page}
    if query:
        params["query"] = query
    try:
        response = requests.get(url, headers=_get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 401:
             raise APIError("Invalid API key or unauthorized access.")
        raise APIError(f"Failed to fetch users: {str(e)}")

def get_user_by_id(user_id: int):
    url = f"{API_BASE_URL}/api/v1/users/{user_id}"
    try:
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 404:
             raise APIError(f"User with ID {user_id} not found.")
        raise APIError(f"Failed to fetch user: {str(e)}")
    
def get_shop():
    url = f"{API_BASE_URL}/api/v1/store"
    try:
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 401:
            raise APIError("Invalid API key or unauthorized access.")
        raise APIError(f"Failed to fetch shop items: {str(e)}")

def get_projects(page: int = 1, query: str = None):
    url = f"{API_BASE_URL}/api/v1/projects"
    params = {"page": page}
    if query:
        params["query"] = query
    try:
        response = requests.get(url, headers=_get_headers(), params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 401:
             raise APIError("Invalid API key or unauthorized access.")
        raise APIError(f"Failed to fetch projects: {str(e)}")

def get_project(project_id: int):
    url = f"{API_BASE_URL}/api/v1/projects/{project_id}"
    try:
        response = requests.get(url, headers=_get_headers())
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 404:
             raise APIError(f"Project with ID {project_id} not found.")
        raise APIError(f"Failed to fetch project: {str(e)}")

def create_project(title: str, description: str, repo_url: str = None, demo_url: str = None, readme_url: str = None):
    url = f"{API_BASE_URL}/api/v1/projects"
    project_data = {
        "title": title,
        "description": description,
    }
    if repo_url:
        project_data["repo_url"] = repo_url
    if demo_url:
        project_data["demo_url"] = demo_url
    if readme_url:
        project_data["readme_url"] = readme_url
    
    body = {"project": project_data}
    
    try:
        response = requests.post(url, headers=_get_headers(), json=body)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 401:
             raise APIError("Invalid API key or unauthorized access.")
        if isinstance(e, requests.HTTPError) and e.response.status_code == 422:
             raise APIError("Invalid project data. Make sure title and description are provided.")
        if isinstance(e, requests.HTTPError) and e.response.status_code == 500:
             raise APIError("Server error. The API may be experiencing issues, please try again later.")
        raise APIError(f"Failed to create project: {str(e)}")

def update_project(project_id: int, title: str = None, description: str = None, repo_url: str = None, demo_url: str = None, readme_url: str = None):
    url = f"{API_BASE_URL}/api/v1/projects/{project_id}"
    project_data = {}
    if title is not None:
        project_data["title"] = title
    if description is not None:
        project_data["description"] = description
    if repo_url is not None:
        project_data["repo_url"] = repo_url
    if demo_url is not None:
        project_data["demo_url"] = demo_url
    if readme_url is not None:
        project_data["readme_url"] = readme_url
    
    body = {"project": project_data}
    
    try:
        response = requests.patch(url, headers=_get_headers(), json=body)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        if isinstance(e, requests.HTTPError) and e.response.status_code == 401:
             raise APIError("Invalid API key or unauthorized access.")
        if isinstance(e, requests.HTTPError) and e.response.status_code == 404:
             raise APIError(f"Project with ID {project_id} not found.")
        if isinstance(e, requests.HTTPError) and e.response.status_code == 500:
             raise APIError("Server error. The API may be experiencing issues, please try again later.")
        raise APIError(f"Failed to update project: {str(e)}")