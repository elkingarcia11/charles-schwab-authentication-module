# Schwab API Authenticator

A Python class for handling Charles Schwab API authentication with fresh token generationthat will be utilized for our trading and analysis bot.

## Features

- 🔐 **OAuth 2.0 Authentication**: Complete implementation of Schwab API OAuth flow
- 🔄 **Fresh Tokens Every Time**: Always gets fresh tokens when you run the program
- 💾 **Token Persistence**: Saves refresh tokens to file for reference
- 🛡️ **Error Handling**: Robust error handling for API calls
- 🎯 **Easy Integration**: Simple class-based design for easy integration into larger projects
- ⚡ **Always Fresh**: Assumes you want fresh tokens every time you run it

## Prerequisites

- Python 3.6+
- Charles Schwab Developer Account
- Registered Schwab API Application

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd schwab_api_authenticator
```

2. Install required dependencies:

```bash
pip install requests python-dotenv
```

3. Create a `.env` file in the project root:

```env
SCHWAB_APP_KEY=your_app_key_here
SCHWAB_APP_SECRET=your_app_secret_here
```

## Setup

### 1. Get Schwab API Credentials

1. Visit the [Charles Schwab Developer Portal](https://developer.schwab.com/)
2. Create a developer account
3. Register a new application
4. Note your App Key and App Secret
5. Set your redirect URI to `https://127.0.0.1`

### 2. Configure Environment Variables

Create a `.env` file with your credentials:

```env
SCHWAB_APP_KEY=your_schwab_app_key
SCHWAB_APP_SECRET=your_schwab_app_secret
```

## Usage

### Basic Usage

```python
from schwab_auth import SchwabAuth

# Create an instance
schwab_auth = SchwabAuth()

# Get fresh access tokens (will prompt for authentication)
access_token = schwab_auth.get_valid_access_token()

if access_token:
    print("Successfully authenticated!")
    # Use the access token for API calls
else:
    print("Authentication failed")
```

### Get Fresh Tokens

```python
# Get fresh tokens (this is what the program always does)
schwab_auth = SchwabAuth()
refresh_token = schwab_auth.automated_token_management()
```

## How It Works

### Authentication Flow

1. **Fresh Token Request**: Every time you run the program, it generates a new authorization URL
2. **User Authorization**: User visits the URL, logs in, and authorizes the application
3. **Code Exchange**: The authorization code is exchanged for access and refresh tokens
4. **Token Storage**: Refresh token is saved to `schwab_refresh_token.txt`
5. **Access Token**: Fresh access token is generated and returned

### Token Management

The system always prompts for fresh token authentication every time you run it. This ensures you always have the most current tokens and eliminates any token expiration issues.

## File Structure

```
schwab_api_authenticator/
├── schwab_auth.py          # Main authentication class
├── schwab_refresh_token.txt # Stored refresh token (auto-generated)
├── .env                    # Environment variables (you create this)
├── .env.example           # Example environment file
└── README.md              # This file
```

## Class Methods

### `SchwabAuth`

#### `__init__()`

Initializes the authenticator with credentials from environment variables.

#### `get_valid_access_token()`

Main method to get fresh access tokens. Always prompts for new authentication.

#### `save_refresh_token(refresh_token)`

Saves refresh token to file for reference.

#### `get_authorization_url(app_key, redirect_uri)`

Generates the authorization URL for user login.

#### `get_tokens_from_code(authorization_code, app_key, app_secret, redirect_uri)`

Exchanges authorization code for tokens.

#### `refresh_access_token(refresh_token, app_key, app_secret)`

Refreshes access token using refresh token.

#### `automated_token_management()`

Handles the complete fresh token generation workflow.

## Environment Variables

| Variable            | Description                    | Required |
| ------------------- | ------------------------------ | -------- |
| `SCHWAB_APP_KEY`    | Your Schwab application key    | Yes      |
| `SCHWAB_APP_SECRET` | Your Schwab application secret | Yes      |

## Error Handling

The class includes comprehensive error handling for:

- Missing environment variables
- API request failures
- Invalid authorization codes
- Token refresh failures
- File I/O errors

## Security Notes

- Never commit your `.env` file to version control
- Keep your App Key and App Secret secure
- The refresh token file contains sensitive data - protect it accordingly
- Use HTTPS in production environments

## Troubleshooting

### Common Issues

1. **"No valid refresh token available"**

   - Solution: This shouldn't happen as the program always gets fresh tokens, but if it does, just run the program again

2. **"Error getting tokens"**

   - Check your App Key and App Secret
   - Ensure the redirect URI matches your app configuration
   - Verify the authorization code is complete and unmodified

3. **"Failed to get access token"**
   - Try running the program again to get fresh tokens
   - Check your internet connection and API credentials

### Debug Mode

For debugging, you can add print statements or modify the error messages in the class methods.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This tool is for educational and development purposes. Always follow Charles Schwab's API terms of service and rate limiting guidelines.

## Support

For issues related to:

- **Schwab API**: Contact Charles Schwab Developer Support
- **This Tool**: Open an issue in this repository

## Changelog

### v1.0.0

- Initial release with class-based architecture
- Always gets fresh tokens on every run
- Token persistence for reference
- Comprehensive error handling
