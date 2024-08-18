from typing import Protocol, Callable
from flask import Flask
from fasthtml import FastHTML

WebFrameApp = Flask | FastHTML

class OAuthMaker(Protocol):
    provider: str
    client_id: str
    client_secret: str
    authorization_base_url: str
    token_url: str
    config: dict
    metadata: dict
    login_required: Callable | None

    def make_oauth_routes(self, ):
        ...