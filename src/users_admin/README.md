# User Admin Module

This module provides functionality for managing user accounts and authentication in a web application.


**Note:** The callback URL for OAuth providers must be set to `http://localhost:8000/users/login/callback`.

## Features

- User authentication via OAuth2 (GitHub and Google providers)
- User data management (create, update, delete, get)
- Role-based access control
- User status management

## Components

1. OAuth Providers:
   - GitHub OAuth (`github_provider.py`)
   - Google OAuth (`google_provider.py`)

2. Data Models:
   - User data model (`data_model.py`)
   - User data types (`userdata.py`)

3. Actions:
   - User management actions (`action.py`)

## Usage

### Setting up OAuth

1. Initialize the OAuth provider:


## API

### OAuth Routes

- `/users/login_action`: Initiates the OAuth login process
- `/users/login/callback`: OAuth callback URL
- `/users/profile`: Fetches the user's profile information
- `/users/profile/emails`: Fetches the user's email information
- `/users/logout_action`: Logs out the user
- `/users/get_userdata`: Retrieves the user's data

### User Management Functions

- `create_user(user_provider: UserProvider, user_data: UserDataProxy)`
- `update_user(user_id: str, user_data: UserDataProxy)`
- `delete_user(user_id: str)`
- `get_user(user_id: str)`

## Data Models

- `UserProvider`: Enum for supported authentication providers
- `UserRole`: Enum for user roles (admin, user, guest)
- `UserStatus`: Enum for user status (active, inactive, banned, deleted)
- `UserDataProxy`: Pydantic model for user data

## Dependencies

- Flask
- Pydantic
- requests_oauthlib
- python-dotenv

## Configuration

Ensure that you have set up the necessary environment variables for OAuth providers. You can use a `.env` file or set them directly in your environment.

## Security Notes

- Always use HTTPS in production to protect OAuth tokens and user data.
- Implement proper error handling and logging in production environments.
- Regularly update dependencies to patch security vulnerabilities.

## Contributing

Please read CONTRIBUTING.md for details on our code of conduct and the process for submitting pull requests.

## License

This project is licensed under the MIT License - see the LICENSE.md file for details.

