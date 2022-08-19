from typing import Union, Any
from pydantic import Field

from .fields import Path, Header, Query, Body, Form, FormURLEncoded, File

_ParamsClasses = (Path, Header, Query, Body, Form, FormURLEncoded, File)
ParamsType = Union[Path, Header, Query, Body, Form, FormURLEncoded, File]
_BodyClasses = (Body, Form, FormURLEncoded, File)
_FormClasses = (Form, FormURLEncoded, File)
FormType = Union[Form, FormURLEncoded, File]

class ParamSignature():
    def __init__(
        self,
        _name: str,
        _type: Any,
        _param_object: ParamsType
    ) -> None:
        self._name = _name
        self._type = _type
        self._default = _param_object.default
        self.param_object = _param_object
        self.param_object.dtype = _type
    
    def __repr__(self) -> str:
        return f"ParamSignature(name={self._name}, type={self._type}, default={self._default}, param_object={self.param_object})"
    
    @property
    def field(self):
        return self.param_object