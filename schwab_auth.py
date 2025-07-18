import base64
import os
import urllib.parse
import requests
import sys
import argparse
from datetime import datetime
from dotenv import load_dotenv

sys.path.append(os.path.join(os.path.dirname(__file__), 'gcs-python-module'))
from gcs_client import GCSClient


class SchwabAuth:
    def __init__(self):
        # load .env file to environment
        load_dotenv()

        # Your Schwab credentials
        self.APP_KEY = os.getenv('SCHWAB_APP_KEY')
        self.APP_SECRET = os.getenv('SCHWAB_APP_SECRET')

        # Schwab API URLs
        self.AUTH_URL = 'https://api.schwabapi.com/v1/oauth/authorize'
        self.TOKEN_URL = 'https://api.schwabapi.com/v1/oauth/token'
        self.REDIRECT_URI = 'https://127.0.0.1'

        # Token storage file
        self.REFRESH_TOKEN_FILE = 'schwab_refresh_token.txt'

        # GCS config
        self.GCS_BUCKET_NAME = os.getenv('GCS_BUCKET_NAME')
        self.gcs_client = GCSClient() if self.GCS_BUCKET_NAME else None

    def save_refresh_token(self, refresh_token):
        """Save refresh token to file"""
        with open(self.REFRESH_TOKEN_FILE, 'w') as f:
            f.write(refresh_token)
        print(f"Refresh token saved to {self.REFRESH_TOKEN_FILE}")

    def load_refresh_token(self):
        """Load refresh token from file if it exists"""
        if os.path.exists(self.REFRESH_TOKEN_FILE):
            with open(self.REFRESH_TOKEN_FILE, 'r') as f:
                return f.read().strip()
        return None

    def upload_refresh_token_to_gcs(self):
        if self.gcs_client and self.GCS_BUCKET_NAME:
            self.gcs_client.upload_file(self.GCS_BUCKET_NAME, self.REFRESH_TOKEN_FILE, self.REFRESH_TOKEN_FILE)

    def download_refresh_token_from_gcs(self):
        if self.gcs_client and self.GCS_BUCKET_NAME:
            print(f"Downloading refresh token from GCS bucket: {self.GCS_BUCKET_NAME}")
            success = self.gcs_client.download_file(self.GCS_BUCKET_NAME, self.REFRESH_TOKEN_FILE, self.REFRESH_TOKEN_FILE)
            if success:
                print(f"Downloaded refresh token to {self.REFRESH_TOKEN_FILE}")
                return self.load_refresh_token()
            else:
                print("Failed to download refresh token from GCS.")
        return None

    def get_authorization_url(self, app_key, redirect_uri):
        """Step 1: Get authorization URL for user login"""
        params = {
            'client_id': app_key,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': 'readonly'
        }

        auth_url = f"{self.AUTH_URL}?" + urllib.parse.urlencode(params)
        return auth_url

    def get_tokens_from_code(self, authorization_code, app_key, app_secret, redirect_uri):
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

        response = requests.post(self.TOKEN_URL, headers=headers, data=data)

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

    def refresh_access_token(self, refresh_token, app_key, app_secret):
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

        response = requests.post(self.TOKEN_URL, headers=headers, data=data)

        if response.status_code == 200:
            return response.json()['access_token']
        else:
            print(
                f"Error refreshing token: {response.status_code} - {response.text}")
            return None

    def automated_token_management(self):
        """Get fresh tokens - always prompts for new authentication"""
        print("=== GETTING FRESH TOKENS ===")
        print("Getting new Schwab tokens...")

        # Get authorization URL
        auth_url = self.get_authorization_url(self.APP_KEY, self.REDIRECT_URI)

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
        tokens = self.get_tokens_from_code(
            auth_code, self.APP_KEY, self.APP_SECRET, self.REDIRECT_URI)

        if tokens:
            self.save_refresh_token(tokens['refresh_token'])
            self.upload_refresh_token_to_gcs()
            print("✅ Tokens obtained and uploaded to GCS successfully!")
            return tokens['refresh_token']
        else:
            print("❌ Failed to get tokens")
            return None

    def get_valid_access_token(self, use_gcs_refresh_token=False):
        """Get a valid access token, using GCS refresh token if specified"""
        if use_gcs_refresh_token:
            refresh_token = self.load_refresh_token()
            if not refresh_token:
                refresh_token = self.download_refresh_token_from_gcs()
            if not refresh_token:
                print("No valid refresh token available locally or in GCS.")
                return None
        else:
            refresh_token = self.automated_token_management()
            if not refresh_token:
                print("No valid refresh token available")
                return None

        # Get fresh access token
        access_token = self.refresh_access_token(
            refresh_token, self.APP_KEY, self.APP_SECRET)

        if not access_token:
            print("Failed to get access token")
            return None

        return access_token


def main():
    parser = argparse.ArgumentParser(description="Schwab API Authenticator")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--authenticate', action='store_true', help='Authenticate locally and upload refresh token to GCS (default)')
    group.add_argument('--get-access-token', action='store_true', help='Get access token using refresh token from GCS')
    args = parser.parse_args()

    schwab_auth = SchwabAuth()

    if args.get_access_token:
        access_token = schwab_auth.get_valid_access_token(use_gcs_refresh_token=True)
        if access_token:
            print(f"Access Token: {access_token}")
        else:
            print("Failed to retrieve access token using GCS refresh token.")
    else:
        # Default: authenticate locally and upload refresh token to GCS
        access_token = schwab_auth.get_valid_access_token(use_gcs_refresh_token=False)
        if access_token:
            print(f"Access Token: {access_token}")
        else:
            print("Failed to authenticate and upload refresh token.")

if __name__ == "__main__":
    main()