import os
from functools import wraps
from datetime import datetime, timedelta
from requests_oauthlib import OAuth2Session
from fasthtml import FastHTML
from flask import Flask
import flask
from flask.json import jsonify
from dotenv import load_dotenv

load_dotenv()

from users_admin.provides.userdata import Userdata
from users_admin.provides.apptypes import WebFrameApp
from users_admin.provides.providertpyes import ProviderType

app = Flask(__name__)


GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_AUTHORIZATION_BASE_URL = os.getenv("GOOGLE_AUTHORIZATION_BASE_URL")
GOOGLE_TOKEN_URL = os.getenv("GOOGLE_TOKEN_URL")


class GoogleOAuthMaker:
    def __init__(self, app: WebFrameApp, config: dict = {}, *args, **kwargs):
        """
        Initialize the GoogleOAuthMaker.

        This class sets up OAuth2 authentication with Google for a Flask application.

        Args:
            app (Flask): The Flask application instance.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Attributes:
            app (Flask): The Flask application instance.
            client_id (str): Google OAuth client ID.
            client_secret (str): Google OAuth client secret.
            authorization_base_url (str): Google's authorization URL.
            token_url (str): Google's token URL.
            metadata (dict): A dictionary to store OAuth-related metadata.
        """
        super().__init__(*args, **kwargs)
        self.provider: ProviderType = "google"
        self.app = app
        self.client_id = GOOGLE_CLIENT_ID
        self.client_secret = GOOGLE_CLIENT_SECRET
        self.authorization_base_url = GOOGLE_AUTHORIZATION_BASE_URL
        self.token_url = GOOGLE_TOKEN_URL
        self.config = config
        self.metadata = {}
        self.login_required = None
        self.url_prefix = "/users"

    def make_oauth_routes(self):
        if isinstance(self.app, Flask):

            @self.app.route(
                self.url_prefix + self.config.get("routes", {}).get("login_action", "/login_action")
            )
            def login_action():
                # Check if the user is already authenticated
                if "oauth_token" in flask.session:
                    flask.session.clear()

                # Step 1: User Authorization.
                google = OAuth2Session(
                    self.client_id,
                    scope=[
                        "https://www.googleapis.com/auth/userinfo.email",
                        "https://www.googleapis.com/auth/userinfo.profile",
                    ],
                    redirect_uri="http://localhost:8010"
                    + self.url_prefix + self.config.get("routes", {}).get(
                        "callback", "/login/callback"
                    ),
                )
                authorization_url, state = google.authorization_url(
                    self.authorization_base_url
                )

                # State is used to prevent CSRF, keep this for later.
                flask.session["oauth_state"] = state
                return flask.redirect(authorization_url)

            # Step 2: User authorization, this happens on the provider.
            @self.app.route(
                self.url_prefix + self.config.get("routes", {}).get(
                    "callback", "/login/callback"
                ),
                methods=["GET"],
            )
            def callback():
                """Step 3: Retrieving an access token.

                The user has been redirected back from the provider to your registered
                callback URL. With this redirection comes an authorization code included
                in the redirect URL. We will use that to obtain an access token.
                """

                google = OAuth2Session(
                    self.client_id,
                    state=flask.session["oauth_state"],
                    redirect_uri="http://localhost:8010"
                    + self.url_prefix + self.config.get("routes", {}).get(
                        "callback", "/login/callback"
                    ),
                )
                token = google.fetch_token(
                    self.token_url,
                    client_secret=self.client_secret,
                    authorization_response=flask.request.url,
                    expires_in=3600 * 2,
                )

                # At this point you can fetch protected resources but lets save
                # the token and show how this is done from a persisted token
                # in /profile.
                flask.session["oauth_token"] = token

                return flask.redirect(flask.url_for(".profile"))

            @self.app.route(
                self.url_prefix + self.config.get("routes", {}).get("profile", "/profile"),
                methods=["GET"],
            )
            def profile():
                """Fetching a protected resource using an OAuth 2 token."""
                try:
                    google = OAuth2Session(
                        self.client_id, token=flask.session["oauth_token"]
                    )
                    return jsonify(
                        google.get(
                            "https://www.googleapis.com/oauth2/v1/userinfo"
                        ).json()
                    )
                except Exception as e:
                    flask.session.clear()
                    return flask.redirect(flask.url_for(".login_action"))

            @self.app.route(
                self.url_prefix + self.config.get("routes", {}).get("logout_action", "/logout_action"),
                methods=["GET"],
            )
            def logout_action():
                """Logout the user."""
                if "oauth_token" in flask.session:
                    # Google doesn't provide a specific endpoint to revoke tokens
                    # You might want to implement additional logic here if needed
                    pass
                # Clear the local session
                flask.session.clear()
                # Redirect to home or login page
                return flask.redirect(flask.url_for(".login_action"))

            @self.app.route(
                self.url_prefix + self.config.get("routes", {}).get(
                    "get_userdata", "/get_userdata"
                ),
                methods=["GET"],
            )
            def get_userdata():
                try:
                    google = OAuth2Session(
                        self.client_id, token=flask.session["oauth_token"]
                    )
                    user_info = google.get("https://www.googleapis.com/oauth2/v1/userinfo").json()
                    provider = self.provider
                    provider_user_id = str(user_info.get("id", ""))
                    email = user_info.get("email", "")
                    name = user_info.get("name", "")
                    avatar_url = user_info.get("picture", "")
                    provider_unique_id = provider + ":" + provider_user_id
                    return Userdata(
                        provider=provider,
                        provider_user_id=provider_user_id,
                        provider_unique_id=provider_unique_id,
                        email=email,
                        name=name,
                        avatar_url=avatar_url,
                    ).model_dump()
                except Exception as e:
                    flask.session.clear()
                    return jsonify({"error": str(e)}), 500

            @self.app.route(
                self.url_prefix + self.config.get("routes", {}).get(
                    "profile_emails", "/profile/emails"
                ),
                methods=["GET"],
            )
            def profile_emails():
                """Fetching user's email information using an OAuth 2 token."""
                try:
                    google = OAuth2Session(
                        self.client_id, token=flask.session["oauth_token"]
                    )
                    user_info = google.get("https://www.googleapis.com/oauth2/v1/userinfo").json()
                    # For Google, the email is typically included in the main user info
                    # We'll return it in a format similar to GitHub's for consistency
                    email_data = [{
                        "email": user_info.get("email", ""),
                        "primary": True,
                        "verified": user_info.get("verified_email", False)
                    }]
                    return jsonify(email_data)
                except Exception as e:
                    flask.session.clear()
                    return flask.redirect(flask.url_for(".login_action"))

        def login_required(self, func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Check if the token exists
                if "oauth_token" not in flask.session:
                    return flask.redirect(
                        flask.url_for(".login_action", next=flask.request.url)
                    )

                # Check token expiration
                token = flask.session["oauth_token"]
                if (
                    "expires_at" in token
                    and datetime.fromtimestamp(token["expires_at"]) < datetime.now()
                ):
                    # Token has expired, clear session and redirect to login
                    flask.session.clear()
                    return flask.redirect(
                        flask.url_for(".login_action", next=flask.request.url)
                    )

                # Optionally, refresh the token if it's close to expiration
                if "expires_at" in token and datetime.fromtimestamp(
                    token["expires_at"]
                ) - datetime.now() < timedelta(minutes=5):
                    try:
                        google = OAuth2Session(
                            self.client_id,
                            state=flask.session["oauth_state"],
                            redirect_uri="http://localhost:8010"
                            + self.config.get("routes", {}).get(
                                "callback", "/login/callback"
                            ),
                        )
                        token = google.fetch_token(
                            self.token_url,
                            client_secret=self.client_secret,
                            authorization_response=flask.request.url,
                            expires_in=3600 * 2,
                        )
                        flask.session["oauth_token"] = token
                    except Exception as e:
                        app.logger.error(f"Token refresh failed: {str(e)}")
                        flask.session.clear()
                        return flask.redirect(
                            flask.url_for(".login_action", next=flask.request.url)
                        )

                # Check for required scopes (if applicable)
                # required_scopes = app.config.get('REQUIRED_SCOPES', [])
                # if not all(scope in token.get('scope', '').split() for scope in required_scopes):
                #     return flask.abort(403, description="Insufficient permissions")

                return func(*args, **kwargs)

            return wrapper


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    google_oauth_maker = GoogleOAuthMaker(app)
    google_oauth_maker.make_oauth_routes()
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    app.secret_key = "1234567890"
    app.run(debug=True, host="0.0.0.0", port=8010)
