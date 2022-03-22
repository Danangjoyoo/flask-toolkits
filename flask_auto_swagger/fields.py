import typing as t
import enum
from pydantic import BaseModel
from pydantic.fields import Undefined

class _request_param_type(enum.Enum):
    path = "path"
    header = "header"
    query = "query"
    body = "body"

class BaseParams():
    """Define parameter implicitly as a Header, Path, Query, Body

    :param default: default value of header
    :param alias: swagger alias
    :param title: swagger title
    :param description: swagger description
    :param gt: greater than `>`
    :param ge: greater equals `>=`
    :param lt: less than `<`
    :param le: less equals `<=`
    :param min_length: min characters for `string` type
    :param max_length: max characters for `string` type
    :param regex:
    :param example: swagger request example
    :param examples:
    :param deprecated: swagger deprecated status
    """
    def __init__(
        self,
        default: t.Any,
        *,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        deprecated: t.Optional[bool] = None,
        _type: _request_param_type = ...,
        **extra: t.Any,
    ) -> None:
        self.default = default
        self.alias = alias
        self.title = title
        self.description = description
        self.gt = gt
        self.ge = ge
        self.lt = lt
        self.le = le
        self.min_length = min_length
        self.max_length = max_length
        self.regex = regex
        self.example = example
        self.examples = examples
        self.deprecated = deprecated
        self.extra = extra
        self.dtype = type(default)
        self._type = _type
    
    def __repr__(self) -> str:
        return str(self.default)

class Header(BaseParams):
    def __init__(
        self,
        default: t.Any,
        *,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        deprecated: t.Optional[bool] = None,
        **extra: t.Any
    ) -> None:
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            example=example,
            examples=examples,
            deprecated=deprecated,
            _type = _request_param_type.header,
            **extra
        )

class Query(BaseParams):
    def __init__(
        self,
        default: t.Any,
        *,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        deprecated: t.Optional[bool] = None,
        **extra: t.Any
    ) -> None:
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            example=example,
            examples=examples,
            deprecated=deprecated,
            _type = _request_param_type.query,
            **extra
        )

class Path(BaseParams):
    def __init__(
        self,
        default: t.Any,
        *,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        deprecated: t.Optional[bool] = None,
        **extra: t.Any
    ) -> None:
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            example=example,
            examples=examples,
            deprecated=deprecated,
            _type = _request_param_type.path,
            **extra
        )

class Body(BaseParams):
    def __init__(
        self,
        default: t.Any,
        *,
        alias: t.Optional[str] = None,
        title: t.Optional[str] = None,
        description: t.Optional[str] = None,
        gt: t.Optional[float] = None,
        ge: t.Optional[float] = None,
        lt: t.Optional[float] = None,
        le: t.Optional[float] = None,
        min_length: t.Optional[int] = None,
        max_length: t.Optional[int] = None,
        regex: t.Optional[str] = None,
        example: t.Any = Undefined,
        examples: t.Optional[t.Dict[str, t.Any]] = None,
        deprecated: t.Optional[bool] = None,
        pydantic_model: BaseModel = ...,
        **extra: t.Any
    ) -> None:
        super().__init__(
            default=default,
            alias=alias,
            title=title,
            description=description,
            gt=gt,
            ge=ge,
            lt=lt,
            le=le,
            min_length=min_length,
            max_length=max_length,
            regex=regex,
            example=example,
            examples=examples,
            deprecated=deprecated,
            _type = _request_param_type.body,
            **extra
        )
        self.pydantic_model = pydantic_model