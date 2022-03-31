from collections import defaultdict
import enum
import json
import os, inspect
import typing as t
from typing import Any, Callable, Dict, Mapping, List, Tuple, Union, Optional
from flask import Flask, Blueprint, Response, jsonify, request, Request
from flask.scaffold import _sentinel
from pydantic import BaseModel, create_model
import pydantic

from .exceptions import SwaggerPathError
from .dependencies import Depends
from .schemas import BaseSchema
from .params import (
    _ParamsClass,
    ParamsType,
    ParamSignature,
    Header,
    Path,
    Query,
    Body
)


class EndpointDefinition():
    """Define endpoint's properties that will be generated by `AutoSwagger`

    :param rule: endpoint path
    :param method: HTTP method [`GET`,`POST`, `PUT`, `DELETE`, `PATCH`]
    :param paired_params: paired argument key - http parameters [`PATH`, `HEADER`, `QUERY`, `BODY`]
    :param tags: endpoint's swagger tags
    :param summary: endpoint's swagger summary
    :param description: endpoint's swagger description
    :param response_description: endpoint's swagger response_description
    :param responses: endpoint's swagger responses
    :param auto_swagger: set this `True` will generate the endpoint swagger automatically using `AutoSwagger`
    :param custom_swagger: put your custom swagger definition
        - this variable will replace the `AutoSwagger` definition only
        for this endpoin
        - this will also removing swagger `tags` so you have to define the tags
        in it
        - example format :
            {
                "tags":[],
                "summary": "My endpoint,
                "parameters": [],
                "responses": {}
            }
    :param pydantic_model: 
    """
    _all_endpoints = []

    def __init__(
        self,
        rule: str,
        method: str,
        paired_params: Dict[str, ParamsType],
        tags: Optional[List[str]] = None,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        auto_swagger: bool = True,
        custom_swagger: Optional[Dict[str, Any]] = None,
        pydantic_model: BaseModel = None
    ) -> None:
        self.rule = rule
        self.method = method.lower()
        self.paired_params = paired_params
        self.tags = tags
        self.summary = summary
        self.description = description
        self.response_description = response_description
        self.auto_swagger = auto_swagger
        self.custom_swagger = custom_swagger
        self.pydantic_model = pydantic_model
        if responses:
            self.responses = responses
        else:
            self.responses = {
                "200": {
                        "description": "Successful Response",
                        "content": {
                            "application/json": {
                                "schema": {}
                            }
                        }
                    },
                "422":{
                        "description": "ValidationError",
                        "content": {
                            "application/json": {
                                "example": {
                                    "detail": [
                                        {
                                        "loc": [
                                            "string"
                                        ],
                                        "msg": "string",
                                        "type": "string"
                                        }
                                    ]
                                }
                            }
                        }
                    }
            }
        EndpointDefinition._all_endpoints.append(self)


class APIRouter(Blueprint):
    """A subclass of `flask.Blueprint`.
    Any objects of this class will be registered as a router

    Use this class to make your router automatically documented by `AutoSwagger`

    :param name: The name of the blueprin Will be prepended to each
        endpoint name.
    :param import_name: The name of the blueprint package, usually
        ``__name__``. This helps locate the ``root_path`` for the
        blueprin
    :param static_folder: A folder with static files that should be
        served by the blueprint's static route. The path is relative to
        the blueprint's root path. Blueprint static files are disabled
        by defaul
    :param static_url_path: The url to serve static files from.
        Defaults to ``static_folder``. If the blueprint does not have
        a ``url_prefix``, the app's static route will take precedence,
        and the blueprint's static files won't be accessible.
    :param template_folder: A folder with templates that should be added
        to the app's template search path. The path is relative to the
        blueprint's root path. Blueprint templates are disabled by
        defaul Blueprint templates have a lower precedence than those
        in the app's templates folder.
    :param url_prefix: A path to prepend to all of the blueprint's URLs,
        to make them distinct from the rest of the app's routes.
    :param subdomain: A subdomain that blueprint routes will match on by
        defaul
    :param url_defaults: A dict of default values that blueprint routes
        will receive by defaul
    :param root_path: By default, the blueprint will automatically set
        this based on ``import_name``. In certain situations this
        automatic detection can fail, so the path can be specified
        manually instead.
    :param tags: endpoint's swagger tags
    :param auto_swagger: set this `True` will generate the endpoint 
        swagger automatically using `AutoSwagger`
    """

    _api_routers = {}

    def __init__(
        self,
        name: str,
        import_name: str,
        static_folder: Optional[Union[str, os.PathLike]] = None,
        static_url_path: Optional[str] = None,
        template_folder: Optional[str] = None,
        url_prefix: Optional[str] = None,
        subdomain: Optional[str] = None,
        url_defaults: Optional[dict] = None,
        root_path: Optional[str] = None,
        cli_group: Optional[str] = _sentinel,
        tags: Optional[List[str]] = [],
        auto_swagger: bool = True
    ):
        super().__init__(
            name=name,
            import_name=import_name,
            static_folder=static_folder,
            static_url_path=static_url_path,
            template_folder=template_folder,
            url_prefix=url_prefix,
            subdomain=subdomain,
            url_defaults=url_defaults,
            root_path=root_path,
            cli_group=cli_group
        )
        self.paired_signature: Dict[str, Dict[str, ParamsType]] = {}
        APIRouter._api_routers[name] = self
        self.defined_endpoints = []
        self._is_registered = False
        self._enable_auto_swagger = auto_swagger
        self.tags = tags or [name]

    def register(self, app: Flask, options: dict) -> None:
        name_prefix = options.get("name_prefix", "")
        self_name = options.get("name", self.name)
        name = f"{name_prefix}.{self_name}".lstrip(".")

        if name in app.blueprints:
            existing_at = f" '{name}'" if self_name != name else ""

            if app.blueprints[name] is not self:
                raise ValueError(
                    f"The name '{self_name}' is already registered for"
                    f" a different blueprint{existing_at}. Use 'name='"
                    " to provide a unique name."
                )
            else:
                import warnings

                warnings.warn(
                    f"The name '{self_name}' is already registered for"
                    f" this blueprint{existing_at}. Use 'name=' to"
                    " provide a unique name. This will become an error"
                    " in Flask 2.1.",
                    stacklevel=4,
                )

        first_bp_registration = not any(bp is self for bp in app.blueprints.values())
        first_name_registration = name not in app.blueprints

        app.blueprints[name] = self
        self._got_registered_once = True
        self._is_registered = True
        state = self.make_setup_state(app, options, first_bp_registration)

        if self.has_static_folder:
            state.add_url_rule(
                f"{self.static_url_path}/<path:filename>",
                view_func=self.send_static_file,
                endpoint="static",
            )

        # Merge blueprint data into paren
        if first_bp_registration or first_name_registration:

            def extend(bp_dict, parent_dict):
                for key, values in bp_dict.items():
                    key = name if key is None else f"{name}.{key}"
                    parent_dict[key].extend(values)

            for key, value in self.error_handler_spec.items():
                key = name if key is None else f"{name}.{key}"
                value = defaultdict(
                    dict,
                    {
                        code: {
                            exc_class: func for exc_class, func in code_values.items()
                        }
                        for code, code_values in value.items()
                    },
                )
                app.error_handler_spec[key] = value

            for endpoint, func in self.view_functions.items():
                app.view_functions[endpoint] = func

            extend(self.before_request_funcs, app.before_request_funcs)
            extend(self.after_request_funcs, app.after_request_funcs)
            extend(
                self.teardown_request_funcs,
                app.teardown_request_funcs,
            )
            extend(self.url_default_functions, app.url_default_functions)
            extend(self.url_value_preprocessors, app.url_value_preprocessors)
            extend(self.template_context_processors, app.template_context_processors)

        for deferred in self.deferred_functions:
            deferred(state)

        cli_resolved_group = options.get("cli_group", self.cli_group)

        if self.cli.commands:
            if cli_resolved_group is None:
                app.cli.commands.update(self.cli.commands)
            elif cli_resolved_group is _sentinel:
                self.cli.name = name
                app.cli.add_command(self.cli)
            else:
                self.cli.name = cli_resolved_group
                app.cli.add_command(self.cli)

        for blueprint, bp_options in self._blueprints:
            bp_options = bp_options.copy()
            bp_url_prefix = bp_options.get("url_prefix")

            if bp_url_prefix is None:
                bp_url_prefix = blueprint.url_prefix

            if state.url_prefix is not None and bp_url_prefix is not None:
                bp_options["url_prefix"] = (
                    state.url_prefix.rstrip("/") + "/" + bp_url_prefix.lstrip("/")
                )
            elif bp_url_prefix is not None:
                bp_options["url_prefix"] = bp_url_prefix
            elif state.url_prefix is not None:
                bp_options["url_prefix"] = state.url_prefix

            bp_options["name_prefix"] = name
            blueprint.register(app, bp_options)

    def get(
        self,
        rule: str,
        tags: Optional[List[str]] = [],
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        auto_swagger: bool = True,
        custom_swagger: Optional[Dict[str, Any]] = None,
        **options: Any
    ) -> Callable:
        return self._method_route("GET", rule, options, tags, summary, description, response_description, responses, auto_swagger, custom_swagger)

    def post(
        self,
        rule: str,
        tags: Optional[List[str]] = [],
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        auto_swagger: bool = True,
        custom_swagger: Optional[Dict[str, Any]] = None,
        **options: Any
    ) -> Callable:
        return self._method_route("POST", rule, options, tags, summary, description, response_description, responses, auto_swagger, custom_swagger)
    
    def put(
        self,
        rule: str,
        tags: Optional[List[str]] = [],
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        auto_swagger: bool = True,
        custom_swagger: Optional[Dict[str, Any]] = None,
        **options: Any
    ) -> Callable:
        return self._method_route("PUT", rule, options, tags, summary, description, response_description, responses, auto_swagger, custom_swagger)

    def delete(
        self,
        rule: str,
        tags: Optional[List[str]] = [],
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        auto_swagger: bool = True,
        custom_swagger: Optional[Dict[str, Any]] = None,
        **options: Any
    ) -> Callable:
        return self._method_route("DELETE", rule, options, tags, summary, description, response_description, responses, auto_swagger, custom_swagger)
    
    def patch(
        self,
        rule: str,
        tags: Optional[List[str]] = [],
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        auto_swagger: bool = True,
        custom_swagger: Optional[Dict[str, Any]] = None,
        **options: Any
    ) -> Callable:
        return self._method_route("PATCH", rule, options, tags, summary, description, response_description, responses, auto_swagger, custom_swagger)
    
    def _method_route(
        self,
        method: str,
        rule: str,
        options: dict,
        tags: Optional[List[str]] = [],
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        auto_swagger: bool = True,
        custom_swagger: Optional[Dict[str, Any]] = None,
    ) -> Callable:
        if "methods" in options:
            raise TypeError("Use the 'route' decorator to use the 'methods' argumen")
        return self.route(
            rule=rule,
            methods=[method],
            tags=tags,
            summary=summary,
            description=description,
            response_description=response_description,
            responses=responses,
            auto_swagger=auto_swagger,
            custom_swagger=custom_swagger,
            **options
            )

    def route(
        self,
        rule: str,
        tags: Optional[List[str]] = [],
        summary: Optional[str] = None,
        description: Optional[str] = None,
        response_description: str = "Successful Response",
        responses: Optional[Dict[Union[int, str], Dict[str, Any]]] = None,
        auto_swagger: bool = True,
        custom_swagger: Optional[Dict[str, Any]] = None,
        **options: Any
    ) -> Callable:
        
        def decorator(func: Callable) -> Callable:
            http_method = options["methods"][0]
            paired_params = self._get_func_signature(rule, http_method, func)
            self.paired_signature[self.url_prefix+rule] = paired_params
            pydantic_model = self.generate_endpoint_pydantic(func.__name__+"Schema", func)

            def create_modified_func():
                def modified_func(**paths):
                    try:
                        valid_kwargs = self.get_kwargs(paths, request, paired_params, pydantic_model)
                        valid_kwargs = self.fill_all_enum_value(valid_kwargs)
                        return func(**valid_kwargs)
                    except pydantic.ValidationError as e:
                        return Response(
                            response=json.dumps(e.errors()),
                            status=422,
                            mimetype="application/json"
                            )
                    except Exception as e:
                        raise e
                modified_func.__name__ = func.__name__
                return modified_func

            # register endpoint
            f = create_modified_func()
            endpoint = options.pop("endpoint", None)
            self.add_url_rule(rule, endpoint, f, **options)
            defined_ep = EndpointDefinition(
                rule=self.validate_rule_for_swagger(self.url_prefix+rule),
                method=http_method,
                paired_params=paired_params,
                tags=tags+self.tags,
                summary=summary if summary else func.__name__,
                description=description if description else func.__name__,
                response_description=response_description,
                responses=responses,
                auto_swagger=self._enable_auto_swagger & auto_swagger,
                custom_swagger=custom_swagger,
                pydantic_model=pydantic_model
                )
            self.defined_endpoints.append(defined_ep)
            return func

        return decorator

    def fill_all_enum_value(self, o):
        try:
            datas = {}
            if type(o) == dict:
                for k in o:
                    datas[k] = self.fill_all_enum_value(o[k])
                return datas
            if enum.Enum.__subclasscheck__(o.__class__):
                return o.value
        except:
            return o
        return o

    def extract_signature_params(self, func: Callable):
        """Extract the signature of a function as parameters"""
        annots = func.__annotations__
        fsig = inspect.signature(func)
        default_val = {
            k: v.default if v.default != inspect._empty else ... 
            for k,v in fsig.parameters.items()
            }
        res = {k: (annots[k] if k in annots else str, d) for k, d in default_val.items()}
        return res
    
    def generate_endpoint_pydantic(self, name: str, func: Callable):
        return create_model(name, __base__=BaseSchema, **self.extract_signature_params(func))

    def _get_func_signature(self, path: str, method: str, func: Callable):
        params_signature = inspect.signature(func).parameters
        annots = func.__annotations__
        pair = {}
        for k, p in params_signature.items():
            ## get default value
            if p.default != inspect._empty:
                if type(p.default) not in _ParamsClass:
                    if type(p.default) == Depends:
                        if not p.default.obj:
                            if k in annots:
                                p.default.obj = annots[k]
                        if p.default.obj:
                            pair.update(self._get_func_signature(path, p.default.obj))
                        continue
                    else:
                        default_value = Query(p.default)
                else:
                    default_value = p.default
            else:
                default_value = Query(...)

            ## check path params
            if self.check_params_in_path(k, path):
                default_value = Path(default_value.default)
            
            ## get default type
            if k in annots:
                default_type = annots[k]
            else:
                default_type = str
            
            ## check pydantic annots
            # if default_type.__class__ == t._GenericAlias:
            #     if method.lower() in ["post", "put"]:
            #         for a in default_type.__args__:
            #             if BaseModel.__subclasscheck__(a):
            #                 default_value = Body(default_value.default, pydantic_model=a)
            #                 break

            pair[k] = ParamSignature(k, default_type, default_value)
        return pair

    def validate_rule_for_swagger(self, rule: str):
        if rule.count("<") == rule.count(">"):
            rule = rule.replace("<","{")
            rule = rule.replace(">", "}")
            return rule
        error = f"Invalid use of <path_params> in rule: {rule}"
        raise SwaggerPathError(error)

    def get_kwargs(self, paths: dict, request: Request, paired_params: dict, pydantic_model: BaseSchema):
        """Get keyword args that will be passed to the function
        """
        variables = pydantic_model.__fields__.keys()        
        queries = request.args.to_dict()
        query_kwargs = {k: queries[k] for k in variables if k in queries}
        header_kwargs = {k: request.headers.get(k) for k in variables if request.headers.get(k)}
        kwargs = {**query_kwargs, **header_kwargs, **paths}
        empty_keys = pydantic_model.get_non_exist_var_in_kwargs(**kwargs)
        total_body = self.count_required_body(paired_params)
        if total_body:
            for k in empty_keys:
                if k in paired_params:
                    po = paired_params[k].param_object
                    if type(po) == Body:
                        if BaseModel.__subclasscheck__(po.dtype):
                            if total_body == 1:
                                kwargs[k] = po.dtype(**request.json)
                            else:
                                kwargs[k] = po.dtype(**request.json[k])
        valid_kwargs = pydantic_model(**kwargs)
        return vars(valid_kwargs)

    def count_required_body(self, paired_params: Dict[str, Any]) -> int:
        total = 0
        for pp in paired_params.values():
            po = pp.param_object
            if type(po) == Body:
                total += 1
        return total

    def check_params_in_path(self, key: str, path: str):
        len_path = len(path)
        if key in path:
            len_key = len(key)
            idx = path.find(key)
            if idx+len_key >= len_path:
                error = f"Invalid path. No closing mark '>' in : {path}"
                raise SwaggerPathError(error)
            if path[idx-1] == "<" and path[idx+len_key] == ">":
                return True
        return False