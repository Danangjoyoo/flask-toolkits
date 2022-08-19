import enum
from json import JSONEncoder
import json
from typing import Any, Callable, Iterable, Mapping, Optional, Tuple, Union
from pydantic import BaseModel
from werkzeug.wrappers.response import Response as ResponseBase

class SwaggerJSONEncoder(JSONEncoder):
    def __init__(
        self, 
        *,
        skipkeys: bool = False,
        ensure_ascii: bool = True,
        check_circular: bool = True,
        allow_nan: bool = True,
        sort_keys: bool = False,
        indent: Optional[int] = None,
        separators:  Optional[Tuple[str, str]] = None,
        default: Callable[..., Any] = None
    ) -> None:
        super().__init__(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            sort_keys=sort_keys,
            indent=indent,
            separators=separators,
            default=default,
        )
    
    def default(self, o: Any) -> Any:
        try:
            if BaseModel.__subclasscheck__(o.__class__):
                return o.dict()
            if enum.Enum.__subclasscheck__(o.__class__):
                return o.value
        finally:
            try:
                oo = super().default(o)            
            except:
                oo = o.__repr__()
        return oo

class JSONResponse(ResponseBase):
    def __init__(
        self,
        response: Any = None,
        status_code: Optional[int] = None,
        headers: Optional[
            Union[Mapping[str, Union[str, int, Iterable[Union[str, int]]]],
            Iterable[Tuple[str, Union[str, int]]]]
        ] = None
    ) -> None:
        response = json.dumps(response, cls=SwaggerJSONEncoder)
        super().__init__(response, status_code, headers, mimetype="application/json")


class HTMLResponse(ResponseBase):
    def __init__(
        self,
        response: Any = None,
        status_code: Optional[int] = None,
        headers: Optional[
            Union[Mapping[str, Union[str, int, Iterable[Union[str, int]]]],
            Iterable[Tuple[str, Union[str, int]]]]
        ] = None
    ) -> None:
        response = str(response) if response != None else None
        super().__init__(response, status_code, headers, mimetype="text/html")


class PlainTextResponse(ResponseBase):
    def __init__(
        self,
        response: Any = None,
        status_code: Optional[int] = None,
        headers: Optional[
            Union[Mapping[str, Union[str, int, Iterable[Union[str, int]]]],
            Iterable[Tuple[str, Union[str, int]]]]
        ] = None
    ) -> None:
        response = str(response) if response != None else None
        super().__init__(response, status_code, headers, mimetype="text/plain")