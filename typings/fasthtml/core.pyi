"""
This type stub file was generated by pyright.
"""

from fastcore.utils import *
from fastcore.xml import *
from dataclasses import dataclass
from inspect import Parameter
from starlette.requests import HTTPConnection
from .starlette import *
from starlette.convertors import StringConvertor

__all__ = ['empty', 'htmx_hdrs', 'fh_cfg', 'htmxscr', 'htmxwsscr', 'surrsrc', 'scopesrc', 'viewport', 'charset', 'all_meths', 'is_typeddict', 'is_namedtuple', 'date', 'snake2hyphens', 'HtmxHeaders', 'str2int', 'HttpHeader', 'form2dict', 'flat_xt', 'Beforeware', 'WS_RouteX', 'uri', 'decode_uri', 'RouteX', 'RouterX', 'get_key', 'FastHTML', 'serve', 'cookie', 'reg_re_param', 'MiddlewareBase']
empty = Parameter.empty
def is_typeddict(cls: type) -> bool:
    "Check if `cls` is a `TypedDict`"
    ...

def is_namedtuple(cls): # -> bool:
    "`True` if `cls` is a namedtuple type"
    ...

def date(s: str): # -> datetime:
    "Convert `s` to a datetime"
    ...

def snake2hyphens(s: str): # -> str:
    "Convert `s` from snake case to hyphenated and capitalised"
    ...

htmx_hdrs = ...
@dataclass
class HtmxHeaders:
    boosted: str | None = ...
    current_url: str | None = ...
    history_restore_request: str | None = ...
    prompt: str | None = ...
    request: str | None = ...
    target: str | None = ...
    trigger_name: str | None = ...
    trigger: str | None = ...
    def __bool__(self): # -> bool:
        ...
    


def str2int(s) -> int:
    "Convert `s` to an `int`"
    ...

fh_cfg = ...
@dataclass
class HttpHeader:
    k: str
    v: str
    ...


def form2dict(form: FormData) -> dict:
    "Convert starlette form data to a dict"
    ...

def flat_xt(lst): # -> list[Any]:
    "Flatten lists"
    ...

class Beforeware:
    def __init__(self, f, skip=...) -> None:
        ...
    


class WS_RouteX(WebSocketRoute):
    def __init__(self, path: str, recv, conn: callable = ..., disconn: callable = ..., *, name=..., middleware=..., hdrs=..., before=...) -> None:
        ...
    


def uri(_arg, **kwargs): # -> str:
    ...

def decode_uri(s): # -> tuple[str, dict[Any, Any]]:
    ...

@patch
def to_string(self: StringConvertor, value: str) -> str:
    ...

@patch
def url_path_for(self: HTTPConnection, name: str, **path_params): # -> URLPath:
    ...

_verbs = ...
class RouteX(Route):
    def __init__(self, path: str, endpoint, *, methods=..., name=..., include_in_schema=..., middleware=..., hdrs=..., ftrs=..., before=..., after=..., htmlkw=..., **bodykw) -> None:
        ...
    


class RouterX(Router):
    def __init__(self, routes=..., redirect_slashes=..., default=..., on_startup=..., on_shutdown=..., lifespan=..., *, middleware=..., hdrs=..., ftrs=..., before=..., after=..., htmlkw=..., **bodykw) -> None:
        ...
    
    def add_route(self, path: str, endpoint: callable, methods=..., name=..., include_in_schema=...): # -> None:
        ...
    
    def add_ws(self, path: str, recv: callable, conn: callable = ..., disconn: callable = ..., name=...): # -> None:
        ...
    


htmxscr = ...
htmxwsscr = ...
surrsrc = ...
scopesrc = ...
viewport = ...
charset = ...
def get_key(key=..., fname=...): # -> str:
    ...

class _SessionMiddleware(SessionMiddleware):
    "Same as Starlette's `SessionMiddleware`, but wraps `session` in an AttrDict"
    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        ...
    


class FastHTML(Starlette):
    def __init__(self, debug=..., routes=..., middleware=..., exception_handlers=..., on_startup=..., on_shutdown=..., lifespan=..., hdrs=..., ftrs=..., before=..., after=..., ws_hdr=..., surreal=..., htmx=..., default_hdrs=..., sess_cls=..., secret_key=..., session_cookie=..., max_age=..., sess_path=..., same_site=..., sess_https_only=..., sess_domain=..., key_fname=..., htmlkw=..., **bodykw) -> None:
        ...
    
    def ws(self, path: str, conn=..., disconn=..., name=...): # -> Callable[..., Any]:
        ...
    


@patch
def route(self: FastHTML, path: str = ..., methods=..., name=..., include_in_schema=...): # -> _lf | Callable[..., _lf]:
    "Add a route at `path`; the function name is the default method"
    ...

all_meths = ...
def serve(appname=..., app=..., host=..., port=..., reload=..., reload_includes: list[str] | str | None = ..., reload_excludes: list[str] | str | None = ...): # -> None:
    "Run the app in an async server, with live reload set as the default."
    ...

def cookie(key: str, value=..., max_age=..., expires=..., path=..., domain=..., secure=..., httponly=..., samesite=...): # -> HttpHeader:
    "Create a 'set-cookie' `HttpHeader`"
    ...

def reg_re_param(m, s): # -> None:
    ...

class MiddlewareBase:
    async def __call__(self, scope, receive, send) -> None:
        ...
    


