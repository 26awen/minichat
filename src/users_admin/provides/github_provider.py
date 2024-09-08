import os
from functools import wraps
from datetime import datetime, timedelta
from requests_oauthlib import OAuth2Session
from flask import Flask
import flask
from flask.json import jsonify
from dotenv import load_dotenv

load_dotenv()
from users_admin.provides.userdata import Userdata
from users_admin.provides.apptypes import WebFrameApp
from users_admin.provides.providertpyes import ProviderType

app = Flask(__name__)


GITHUB_CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
GITHUB_CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
GITHUB_AUTHORIZATION_BASE_URL = os.getenv("GITHUB_AUTHORIZATION_BASE_URL")
GITHUB_TOKEN_URL = os.getenv("GITHUB_TOKEN_URL")




class GithubOAuthMaker:
    def __init__(self, app: WebFrameApp, config: dict = {}, *args, **kwargs):
        """
        Initialize the GithubOAuthMaker.

        This class sets up OAuth2 authentication with GitHub for a WebFrameApp application.

        Args:
            app (WebFrameApp): The WebFrameApp application instance.
            *args: Variable length argument list.
            **kwargs: Arbitrary keyword arguments.

        Attributes:
            app (WebFrameApp): The WebFrameApp application instance.
            client_id (str): GitHub OAuth client ID.
            client_secret (str): GitHub OAuth client secret.
            authorization_base_url (str): GitHub's authorization URL.
            token_url (str): GitHub's token URL.
            metadata (dict): A dictionary to store OAuth-related metadata.
        """
        super().__init__(*args, **kwargs)
        self.provider: ProviderType = "github"
        self.app = app
        self.client_id = GITHUB_CLIENT_ID
        self.client_secret = GITHUB_CLIENT_SECRET
        self.authorization_base_url = GITHUB_AUTHORIZATION_BASE_URL
        self.token_url = GITHUB_TOKEN_URL
        self.config = config
        self.metadata = {}

    def make_oauth_routes(self):
        """
        Make OAuth routes for GitHub authentication.
        """
        if isinstance(self.app, Flask):

            @self.app.route(
                self.config.get("routes", {}).get("login", "/login")
            )
            def login():
                # Step 1: User Authorization.

                # Redirect the user/resource owner to the OAuth provider (i.e. Github)
                # using an URL with a few key OAuth parameters.
                github = OAuth2Session(self.client_id, scope=["user:email"])
                authorization_url, state = github.authorization_url(
                    self.authorization_base_url
                )

                # State is used to prevent CSRF, keep this for later.
                flask.session["oauth_state"] = state
                return flask.redirect(authorization_url)

            # Step 2: User authorization, this happens on the provider.
            @self.app.route(
                self.config.get("routes", {}).get(
                    "callback", "/login/callback"
                ),
                methods=["GET"],
            )
            def callback():
                # Step 3: Retrieving an access token.

                # The user has been redirected back from the provider to your registered
                # callback URL. With this redirection comes an authorization code included
                # in the redirect URL. We will use that to obtain an access token.

                github = OAuth2Session(
                    self.client_id,
                    state=flask.session["oauth_state"],
                    redirect_uri="http://localhost:8010"
                    + self.config.get("routes", {}).get(
                        "callback", "/login/callback"
                    ),
                )
                token = github.fetch_token(
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
                self.config.get("routes", {}).get("profile", "/profile"),
                methods=["GET"],
            )
            def profile():
                """Fetching a protected resource using an OAuth 2 token."""
                github = OAuth2Session(
                    self.client_id, token=flask.session["oauth_token"]
                )
                return jsonify(github.get("https://api.github.com/user").json())

            @self.app.route(
                self.config.get("routes", {}).get(
                    "profile_emails", "/profile/emails"
                ),
                methods=["GET"],
            )
            def profile_emails():
                """Fetching a protected resource using an OAuth 2 token."""
                github = OAuth2Session(
                    self.client_id, token=flask.session["oauth_token"]
                )
                return jsonify(
                    github.get("https://api.github.com/user/emails").json()
                )

            @self.app.route(
                self.config.get("routes", {}).get("logout", "/logout"),
                methods=["GET"],
            )
            def logout():
                """Logout the user."""
                github = OAuth2Session(
                    self.client_id, token=flask.session["oauth_token"]
                )
                github.access_token = None
                flask.session.clear()
                return "Logged out"

            @self.app.route(
                self.config.get("routes", {}).get(
                    "get_userdata", "/user/get_userdata"
                ),
                methods=["GET"],
            )
            def get_userdata():
                github = OAuth2Session(
                    self.client_id, token=flask.session["oauth_token"]
                )
                provider = self.provider
                provider_user_id = str(
                    github.get("https://api.github.com/user")
                    .json()
                    .get("id", "")
                )
                email = (
                    github.get("https://api.github.com/user/emails")
                    .json()[0]
                    .get("email", "")
                )
                name = (
                    github.get("https://api.github.com/user")
                    .json()
                    .get("login", "")
                )
                avatar_url = (
                    github.get("https://api.github.com/user")
                    .json()
                    .get("avatar_url", "")
                )
                provider_unique_id = provider + ":" + provider_user_id
                return Userdata(
                    provider=provider,
                    provider_user_id=provider_user_id,
                    provider_unique_id=provider_unique_id,
                    email=email,
                    name=name,
                    avatar_url=avatar_url,
                ).model_dump()

    def login_required(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Check if the token exists
            if "oauth_token" not in flask.session:
                return flask.redirect(
                    flask.url_for(".login", next=flask.request.url)
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
                    flask.url_for(".login", next=flask.request.url)
                )

            # Optionally, refresh the token if it's close to expiration
            if "expires_at" in token and datetime.fromtimestamp(
                token["expires_at"]
            ) - datetime.now() < timedelta(minutes=5):
                try:
                    github = OAuth2Session(
                        self.client_id,
                        state=flask.session["oauth_state"],
                        redirect_uri="http://localhost:8010"
                        + self.config.get("routes", {}).get(
                            "callback", "/login/callback"
                        ),
                    )
                    token = github.fetch_token(
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
                        flask.url_for(".login", next=flask.request.url)
                    )

            # Check for required scopes (if applicable)
            # required_scopes = app.config.get('REQUIRED_SCOPES', [])
            # if not all(scope in token.get('scope', '').split() for scope in required_scopes):
            #     return flask.abort(403, description="Insufficient permissions")

            return func(*args, **kwargs)

        return wrapper


if __name__ == "__main__":
    # This allows us to use a plain HTTP callback
    github_oauth_maker = GithubOAuthMaker(app)
    github_oauth_maker.make_oauth_routes()
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    app.secret_key = "1234567890"
    app.run(debug=True, host="0.0.0.0", port=8010)
