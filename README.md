# Schwab API Authenticator

A Python class for handling Charles Schwab API authentication with fresh token generation every time and automatic cloud storage integration.

## Features

- 🔐 **OAuth 2.0 Authentication**: Complete implementation of Schwab API OAuth flow
- 🔄 **Fresh Tokens Every Time**: Always gets fresh tokens when you run the program
- 💾 **Token Persistence**: Saves refresh tokens to file for reference
- ☁️ **Cloud Storage Integration**: Automatically uploads tokens to Google Cloud Storage
- 🛡️ **Error Handling**: Robust error handling for API calls
- 🎯 **Easy Integration**: Simple class-based design for easy integration into larger projects
- ⚡ **Always Fresh**: Assumes you want fresh tokens every time you run it
- 🔧 **Modular Architecture**: Separate GCS module for cloud storage operations

## Prerequisites

- Python 3.6+
- Charles Schwab Developer Account
- Registered Schwab API Application
- Google Cloud Storage Account (for cloud token storage)

## Installation

1. Clone this repository:

```bash
git clone <repository-url>
cd schwab_api_authenticator
```

2. Create and activate a virtual environment (recommended):

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate

# On Windows:
# venv\Scripts\activate
```

3. Install required dependencies:

```bash
# Ensure pip is up to date
pip install --upgrade pip

# Install dependencies
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:

```env
SCHWAB_APP_KEY=your_app_key_here
SCHWAB_APP_SECRET=your_app_secret_here
GCS_BUCKET_NAME=your_gcs_bucket_name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

## Setup

### 1. Get Schwab API Credentials

1. Visit the [Charles Schwab Developer Portal](https://developer.schwab.com/)
2. Create a developer account
3. Register a new application
4. Note your App Key and App Secret
5. Set your redirect URI to `https://127.0.0.1`

### 2. Set up Google Cloud Storage

1. Create a Google Cloud Storage bucket for token storage
2. Set up a service account with Storage Object Admin permissions
3. Download the service account key (JSON format)
4. Configure the `GOOGLE_APPLICATION_CREDENTIALS` environment variable

### 3. Configure Environment Variables

Create a `.env` file with your credentials:

```env
SCHWAB_APP_KEY=your_schwab_app_key
SCHWAB_APP_SECRET=your_schwab_app_secret
GCS_BUCKET_NAME=your_gcs_bucket_name
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/service-account-key.json
```

## How to Run

### Method 1: Direct Execution

Run the script directly to get fresh access tokens:

```bash
python schwab_auth.py
```

This will:

1. Prompt you to visit the authorization URL
2. Ask you to paste the redirect URL after authorization
3. Generate fresh access and refresh tokens
4. Display the access token for use in your applications
5. **Automatically upload the refresh token to Google Cloud Storage**

### Expected Output

When you run the program, you'll see:

```
=== GETTING FRESH TOKENS ===
Getting new Schwab tokens...

1. Visit this URL: https://api.schwabapi.com/v1/oauth/authorize?client_id=...
2. Log in and authorize the app
3. You'll be redirected to a URL that looks like:
   https://127.0.0.1/?code=LONG_CODE_HERE&session=...
4. Copy the ENTIRE redirect URL

Paste the full redirect URL here: [YOU PASTE THE URL HERE]
Extracted code: ABC123...
Tokens obtained successfully!
Access Token: eyJ0eXAiOiJKV1QiLCJ...
Refresh Token: eyJ0eXAiOiJKV1QiLCJ...
Refresh token saved to schwab_refresh_token.txt
File schwab_refresh_token.txt uploaded to schwab_refresh_token.txt.
✅ Tokens obtained successfully!
```

### Deactivating the Virtual Environment

When you're done working with the project, you can deactivate the virtual environment:

```bash
deactivate
```

## How It Works

### Authentication Flow

1. **Fresh Token Request**: Every time you run the program, it generates a new authorization URL
2. **User Authorization**: User visits the URL, logs in, and authorizes the application
3. **Code Exchange**: The authorization code is exchanged for access and refresh tokens
4. **Token Storage**: Refresh token is saved to `schwab_refresh_token.txt`
5. **Cloud Upload**: Refresh token is automatically uploaded to Google Cloud Storage
6. **Access Token**: Fresh access token is generated and returned

### Token Management

The system always prompts for fresh token authentication every time you run it. This ensures you always have the most current tokens and eliminates any token expiration issues. Additionally, tokens are automatically backed up to Google Cloud Storage for secure storage and easy retrieval.

## File Structure

```
schwab_api_authenticator/
├── schwab_auth.py          # Main authentication class
├── schwab_refresh_token.txt # Stored refresh token (auto-generated)
├── .env                    # Environment variables (you create this)
├── .env.example           # Example environment file
├── requirements.txt       # Main project dependencies
├── README.md              # This file
└── gcs-python-module/     # Google Cloud Storage module
    ├── gcs_client.py      # GCS client class
    ├── requirements.txt   # GCS module dependencies
    ├── env.example        # GCS environment example
    ├── README.md          # GCS module documentation
    └── tests/             # GCS module tests
        ├── integration_test.py
        └── README.md
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

### `GCSClient` (from gcs-python-module)

The GCS client provides comprehensive Google Cloud Storage operations:

- `upload_file(bucket_name, source_file_name, destination_blob_name)` - Upload files to GCS
- `download_file(bucket_name, source_blob_name, destination_file_name)` - Download files from GCS
- `list_files(bucket_name, prefix="")` - List files in a bucket
- `get_file_metadata(bucket_name, blob_name)` - Get file metadata
- `delete_file(bucket_name, blob_name)` - Delete files from GCS
- `create_bucket(bucket_name)` - Create new buckets
- `delete_bucket(bucket_name)` - Delete buckets
- `list_buckets()` - List all buckets
- `bucket_exists(bucket_name)` - Check if bucket exists

## Environment Variables

| Variable                         | Description                               | Required |
| -------------------------------- | ----------------------------------------- | -------- |
| `SCHWAB_APP_KEY`                 | Your Schwab application key               | Yes      |
| `SCHWAB_APP_SECRET`              | Your Schwab application secret            | Yes      |
| `GCS_BUCKET_NAME`                | Your Google Cloud Storage bucket name     | Yes      |
| `GOOGLE_APPLICATION_CREDENTIALS` | Path to your GCS service account key file | Yes      |

## Error Handling

The class includes comprehensive error handling for:

- Missing environment variables
- API request failures
- Invalid authorization codes
- Token refresh failures
- File I/O errors
- Google Cloud Storage operation failures

## Security Notes

- Never commit your `.env` file to version control
- Keep your App Key and App Secret secure
- The refresh token file contains sensitive data - protect it accordingly
- Use HTTPS in production environments
- Store your Google Cloud service account key securely
- Consider using Google Cloud Secret Manager for production deployments

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

4. **Google Cloud Storage Errors**

   - Verify your service account has the correct permissions
   - Check that the bucket name is correct
   - Ensure the service account key file path is correct
   - Verify the bucket exists and is accessible

5. **Virtual Environment Issues**
   - Make sure you've activated the virtual environment before installing dependencies
   - If you see "command not found" errors, ensure the virtual environment is activated
   - If packages aren't found, try reinstalling: `pip install -r requirements.txt`
   - On Windows, use `venv\Scripts\activate` instead of `source venv/bin/activate`

### Debug Mode

For debugging, you can add print statements or modify the error messages in the class methods.

## Google Cloud Storage Module

The project includes a comprehensive Google Cloud Storage module (`gcs-python-module/`) that provides:

- **Service Account Authentication**: Secure authentication using service account keys
- **Comprehensive Operations**: Upload, download, list, delete, and manage files and buckets
- **Error Handling**: Robust error handling with detailed logging
- **Type Hints**: Full type annotation support for better development experience
- **Testing**: Integration tests for all GCS operations

See the [gcs-python-module/README.md](gcs-python-module/README.md) for detailed documentation on the GCS client functionality.

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
- **Google Cloud Storage**: Check the [GCS module documentation](gcs-python-module/README.md)
- **This Tool**: Open an issue in this repository

## Changelog

### v2.0.0

- **Added Google Cloud Storage Integration**: Automatic token upload to GCS
- **Modular Architecture**: Separated GCS functionality into dedicated module
- **Enhanced Security**: Cloud-based token backup and storage
- **Comprehensive GCS Client**: Full GCS operations support
- **Updated Dependencies**: Added Google Cloud Storage requirements

### v1.0.0

- Initial release with class-based architecture
- Always gets fresh tokens on every run
- Token persistence for reference
- Comprehensive error handling
