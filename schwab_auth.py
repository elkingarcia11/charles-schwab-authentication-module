import base64
import os
import urllib.parse
import requests

from datetime import datetime
from dotenv import load_dotenv

# load .env file to environment
load_dotenv()

# Your Schwab credentials
APP_KEY = os.getenv('SCHWAB_APP_KEY')
APP_SECRET = os.getenv('SCHWAB_APP_SECRET')
REDIRECT_URI = os.getenv('SCHWAB_REDIRECT_URI')

# Schwab API URLs
AUTH_URL = 'https://api.schwabapi.com/v1/oauth/authorize'
TOKEN_URL = 'https://api.schwabapi.com/v1/oauth/token'

# Token storage file
TOKEN_FILE = 'schwab_refresh_token.txt'


def save_refresh_token(refresh_token):
    """Save refresh token to file"""
    with open(TOKEN_FILE, 'w') as f:
        f.write(refresh_token)
    print(f"Refresh token saved to {TOKEN_FILE}")


def load_refresh_token():
    """Load refresh token from file"""
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'r') as f:
            return f.read().strip()
    return None


def is_monday():
    """Check if today is Monday"""
    return datetime.now().weekday() == 0


def should_refresh_tokens():
    """Check if we need to refresh tokens (Monday or no token file)"""
    return is_monday() or not os.path.exists(TOKEN_FILE)


def get_authorization_url(app_key, redirect_uri):
    """Step 1: Get authorization URL for user login"""
    params = {
        'client_id': app_key,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'readonly'
    }

    auth_url = f"{AUTH_URL}?" + urllib.parse.urlencode(params)
    return auth_url


def get_tokens_from_code(authorization_code, app_key, app_secret, redirect_uri):
    """Step 2: Exchange authorization code for access and refresh tokens"""

    # Create basic auth header
    credentials = f"{app_key}:{app_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'authorization_code',
        'code': authorization_code,
        'redirect_uri': redirect_uri
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        tokens = response.json()
        print("Tokens obtained successfully!")
        print(f"Access Token: {tokens['access_token'][:20]}...")
        print(f"Refresh Token: {tokens['refresh_token'][:20]}...")
        return tokens
    else:
        print(
            f"Error getting tokens: {response.status_code} - {response.text}")
        return None


def refresh_access_token(refresh_token, app_key, app_secret):
    """Step 3: Refresh access token using refresh token"""

    credentials = f"{app_key}:{app_secret}"
    encoded_credentials = base64.b64encode(credentials.encode()).decode()

    headers = {
        'Authorization': f'Basic {encoded_credentials}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    data = {
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    }

    response = requests.post(TOKEN_URL, headers=headers, data=data)

    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(
            f"Error refreshing token: {response.status_code} - {response.text}")
        return None


def automated_token_management():
    """Automatically handle token refresh on Mondays"""
    if should_refresh_tokens():
        print("=== MONDAY TOKEN REFRESH ===")
        print("Time to refresh your Schwab tokens!")

        # Get authorization URL
        auth_url = get_authorization_url(APP_KEY, REDIRECT_URI)

        # User needs to visit URL and get code
        print(f"\n1. Visit this URL: {auth_url}")
        print("2. Log in and authorize the app")
        print("3. You'll be redirected to a URL that looks like:")
        print("   https://127.0.0.1/?code=LONG_CODE_HERE&session=...")
        print("4. Copy the ENTIRE redirect URL")

        redirect_url = input("\nPaste the full redirect URL here: ").strip()

        # Extract code from URL
        if "code=" in redirect_url:
            auth_code = redirect_url.split("code=")[1].split("&")[0]
            # URL decode the authorization code
            auth_code = urllib.parse.unquote(auth_code)
            print(f"Extracted code: {auth_code[:20]}...")
        else:
            print("Could not find code in URL. Please enter manually:")
            auth_code = input("Enter the authorization code: ").strip()
            auth_code = urllib.parse.unquote(auth_code)

        # Get new tokens
        tokens = get_tokens_from_code(
            auth_code, APP_KEY, APP_SECRET, REDIRECT_URI)

        if tokens:
            save_refresh_token(tokens['refresh_token'])
            print("✅ Tokens refreshed successfully!")
            return tokens['refresh_token']
        else:
            print("❌ Failed to refresh tokens")
            return None
    else:
        print("Using existing refresh token...")
        return load_refresh_token()


def get_valid_access_token():
    """Get a valid access token, handling refresh automatically"""

    # Get refresh token (with automatic Monday refresh)
    refresh_token = automated_token_management()

    if not refresh_token:
        print("No valid refresh token available")
        return None

    # Get fresh access token
    access_token = refresh_access_token(refresh_token, APP_KEY, APP_SECRET)

    if not access_token:
        print("Failed to get access token - may need to refresh tokens")
        return None

    return access_token


if __name__ == "__main__":
    access_token = get_valid_access_token()
