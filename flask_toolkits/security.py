from base64 import b64decode
from abc import ABC, abstractmethod
from flask import request, Request
from typing import Any, Optional
from enum import Enum
from jose import jwt


class HTTPScheme(Enum):
    basic: str = "basic"
    bearer: str = "bearer"


class HTTPSecurityBase(ABC):
    all_schemes = {}

    @abstractmethod
    def __init__(self, scheme_name: str, scheme: HTTPScheme):
        self.scheme_name = scheme_name
        self.scheme = scheme
        HTTPSecurityBase.all_schemes[scheme_name] = {"type": "http", "scheme": scheme.value}
    
    def __call__(self, req: Request) -> Any:
        """
        Override this to enable security check
        """
        return req
    
    def get_authorization_data(self, req: Request):
        auth = req.headers.get("Authorization")
        if auth:
            request_scheme, _, data = auth.partition(" ")
            if request_scheme.lower() == self.scheme.value:
                return data
    
    @property
    def schema(self):
        return {self.scheme_name: []}


class HTTPBasicSecurity(HTTPSecurityBase):
    """
    HTTP security authorization with `basic` username and password scheme

    :params scheme_name: set the security scheme name

    - use `self.decode` to decode the jwt function
    - override it if you dont want to use it


    If you want to enable security scheme, you can inherit this class to override `__call__`.
    This could replacing the use `flask_login` decorator scheme.
    """
    def __init__(self, scheme_name: Optional[str] = None):
        super().__init__(
            scheme_name=scheme_name or self.__class__.__name__,
            scheme=HTTPScheme.basic
        )

    def get_authorization_data(self, req: Request):
        hashed = super().get_authorization_data(req)
        return self.decode(hashed)

    def decode(self, hashed: str):
        unhashed = b64decode(hashed).decode("ascii")
        username, _, password = unhashed.partition(":")
        return {"username": username, "password": password}


class HTTPBearerSecurity(HTTPSecurityBase):
    """
    HTTP security authorization with `bearer` or token scheme

    :params scheme_name: set the security scheme name

    - use `self.decode` to decode the jwt function
    - override it if you dont want to use it
    """
    def __init__(self, scheme_name: Optional[str] = None):
        super().__init__(
            scheme_name=scheme_name or self.__class__.__name__,
            scheme=HTTPScheme.bearer
        )
    
    def decode(token, key, algorithms=None, options=None, audience=None, issuer=None, subject=None, access_token=None):
        """
        JWT Token decode function using `python-jose`
        """
        return jwt.decode(token, key, algorithms, options, audience, issuer, subject, access_token)