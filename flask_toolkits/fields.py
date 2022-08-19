from typing import Optional, Dict, Any
import enum
from pydantic import BaseModel, Field
from pydantic.fields import FieldInfo

class _request_param_type(enum.Enum):
    path = "path"
    header = "header"
    query = "query"
    body = "body"
    form = "form"
    form_url_encoded = "x-www-form-urlencoded"
    file = "file"

class BaseParams(FieldInfo):
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
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = None,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        _type: _request_param_type = ...,
        **extra: Any,
    ) -> None:
        self.__default = default
        self.default = default
        self.title = title
        self.description = description
        self.example = example
        self.examples = examples
        self.deprecated = deprecated
        self.extra = extra
        self.dtype = type(default)
        self._type = _type
        self.__gt = gt
        self.__ge = ge
        self.__lt = lt
        self.__le = le
        self.__min_length = min_length
        self.__max_length = max_length
        self.__regex = regex
        super().__init__(
            default,
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
            repr=repr,
            example=example,
            **extra
        )
        self._validate()        
    
    def __repr__(self) -> str:
        return f"<{self._type.value.upper()} ({str(self.dtype)[8:-2]}) : {self.default}>"
    
    def disable_constraint(self):
        self.default = None
        self.gt = None
        self.ge = None
        self.lt = None
        self.le = None
        self.min_length = None
        self.max_length = None
        self.regex = None
    
    def enable_constaint(self):
        self.default = self.__default
        self.gt = self.__gt
        self.ge = self.__ge
        self.lt = self.__lt
        self.le = self.__le
        self.min_length = self.__min_length
        self.max_length = self.__max_length
        self.regex = self.__regex
    
    def copy(self):
        self_attributes = {
            "alias": self.alias,
            "title": self.title,
            "description": self.description,
            "gt": self.gt,
            "ge": self.ge,
            "lt": self.lt,
            "le": self.le,
            "min_length": self.min_length,
            "max_length": self.max_length,
            "regex": self.regex,
            "example": self.example,
            "examples": self.examples,
            "deprecated": self.deprecated
        }
        self_attributes.update(self.extra)
        return self.__class__(self.__default, **self_attributes)


class Header(BaseParams):
    """Define request parameter implicitly as a Header

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
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = None,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        **extra: Any
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
    """Define request parameter implicitly as a Query

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
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = None,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        **extra: Any
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
    """Define request parameter implicitly as a Path

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
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = None,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        **extra: Any
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
    """Define request parameter implicitly as a Body

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
    :param pydantic_model: pydantic model that represent the body schema
    """
    def __init__(
        self,
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = None,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        pydantic_model: BaseModel = None,
        **extra: Any
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


class Form(BaseParams):
    """Define request parameter implicitly as a Form

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
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = None,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        **extra: Any
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
            _type = _request_param_type.form,
            **extra
        )


class FormURLEncoded(BaseParams):
    """Define request parameter implicitly as a Form URL Encoded

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
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = None,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        **extra: Any
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
            _type = _request_param_type.form_url_encoded,
            **extra
        )


class File(BaseParams):
    """Define request parameter implicitly as a File

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
        default: Any = ...,
        *,
        alias: Optional[str] = None,
        title: Optional[str] = None,
        description: Optional[str] = None,
        gt: Optional[float] = None,
        ge: Optional[float] = None,
        lt: Optional[float] = None,
        le: Optional[float] = None,
        min_length: Optional[int] = None,
        max_length: Optional[int] = None,
        regex: Optional[str] = None,
        example: Any = None,
        examples: Optional[Dict[str, Any]] = None,
        deprecated: Optional[bool] = None,
        **extra: Any
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
            _type = _request_param_type.file,
            **extra
        )