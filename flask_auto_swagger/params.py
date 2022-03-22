import typing as t

from .fields import Path, Header, Query, Body

_ParamsClass = [Header, Query, Path, Body]
ParamsType = t.Union[Header, Query, Path, Body]

class ParamSignature():
    def __init__(
        self,
        _name: str,
        _type: t.Any,
        _param_object: ParamsType
    ) -> None:
        self._name = _name
        self._type = _type
        self._default = _param_object.default
        self.param_object = _param_object
        self.param_object.dtype = _type
