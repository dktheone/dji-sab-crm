# # apps/emp/utils.py
import secrets
import string
import re
import requests
import json
from django.contrib.auth.decorators import login_required, user_passes_test

def role_required(*roles):
    def decorator(view_func):
        @login_required
        @user_passes_test(lambda u: u.groups.filter(name__in=roles).exists())
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator

def generate_random_key(length=10):
    """Generate a secure random alphanumeric key of specified length."""
    characters = string.ascii_letters + string.digits
    return ''.join(secrets.choice(characters) for _ in range(length))


def fetch_ifsc_details(ifsc_code: str) -> dict:
    """
    Fetches IFSC code details from the Razorpay API after validating the IFSC code.

    Args:
        ifsc_code (str): The IFSC code to fetch details for.

    Returns:
        dict: A dictionary containing the IFSC details on success,
              or an 'error' key with a description on failure.
    """
    # Define the standard IFSC code regex pattern
    # It should be 11 characters long
    # First 4 characters: Alphabetic
    # 5th character: 0 (zero)
    # Last 6 characters: Alphanumeric
    ifsc_regex = r"^[A-Z]{4}0[A-Z0-9]{6}$"

    # 1. Validate the IFSC code using regex
    if not re.fullmatch(ifsc_regex, ifsc_code):
        return {
            "error": "Invalid IFSC code format. Please ensure it's 11 characters (first 4 alphabets, 5th is 0, last 6 alphanumeric)."
        }

    # Construct the Razorpay API URL
    api_url = f"https://ifsc.razorpay.com/{ifsc_code}"

    try:
        # 2. Make the API call
        response = requests.get(api_url, timeout=5) # Add a timeout for robustness

        # 3. Check for successful response (status code 200)
        if response.status_code == 200:
            data = response.json()
            # Razorpay API returns a specific error if IFSC is not found
            # It's usually an empty JSON or a specific error message if not found.
            # We'll check for common indicators of a valid response.
            if isinstance(data, dict) and data.get("BANK"):
                return data
            elif isinstance(data, dict) and data.get("error"):
                # Handle specific API-returned errors if any, though Razorpay usually 404s
                return {"error": f"API responded with an error: {data.get('error')}"}
            else:
                # This handles cases where the API returns 200 but no valid data (e.g., empty JSON for invalid IFSC)
                return {"error": f"IFSC code '{ifsc_code}' not found or invalid."}
        elif response.status_code == 404:
            return {"error": f"IFSC code '{ifsc_code}' not found."}
        else:
            # Handle other HTTP error codes
            return {"error": f"API request failed with status code {response.status_code}: {response.text}"}

    except requests.exceptions.Timeout:
        return {"error": "API request timed out. Please try again later."}
    except requests.exceptions.ConnectionError:
        return {"error": "Could not connect to the IFSC API. Check your internet connection."}
    except json.JSONDecodeError:
        return {"error": "Failed to decode JSON response from API."}
    except Exception as e:
        # Catch any other unexpected errors
        return {"error": f"An unexpected error occurred: {str(e)}"}

def log_employee_activity(employee, category, action, remark=None, user=None, ip=None):
    from .models import EmployeeActivityLog
    from config.middleware import get_current_user, get_current_ip

    if user is None:
        user = get_current_user()
    
    if user and not user.is_authenticated:
        user = None

    if ip is None:
        ip = get_current_ip()
        
    EmployeeActivityLog.objects.create(
        employee=employee,
        category=category,
        action=action,
        remark=remark or action,
        performed_by=user,
        ip_address=ip
    )

def get_log_classifications() -> dict:
    """Loads log classification config from log_classification.json."""
    import os
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        json_path = os.path.join(current_dir, 'log_classification.json')
        with open(json_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception:
        return {}
