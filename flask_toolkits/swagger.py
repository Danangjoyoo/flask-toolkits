from collections import defaultdict
import json
import os, enum
from typing import Any, Callable, Dict, Mapping, List, Tuple, Union, Optional
from flask import Blueprint, Flask, jsonify
from flask.scaffold import _sentinel
from flask_swagger_ui import get_swaggerui_blueprint
from pydantic import create_model

from .params import ParamsType, Header, Path, Query, Body
from .routing import APIRouter, EndpointDefinition


class SwaggerGenerator(Blueprint):
    def __init__(
        self,
        title: str = "Auto Swagger",
        name: str = "swagger_generator",
        import_name: str = __name__,
        static_folder: Optional[Union[str, os.PathLike]] = None,
        static_url_path: Optional[str] = None,
        template_folder: Optional[str] = None,
        url_prefix: Optional[str] = None,
        subdomain: Optional[str] = None,
        url_defaults: Optional[dict] = None,
        root_path: Optional[str] = None,
        cli_group: Optional[str] = ...,
        documentation_url: str = "/openapi.json",
        documentation_version: Optional[str] = "1.0.0",
        documentation_description: Optional[str] = "",
        documentation_servers: Optional[List[Dict[str, str]]] = []
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
        self.template = self.create_init_template(
            title=title,
            version=documentation_version,
            description=documentation_description,
            servers=documentation_servers
        )

        @self.get(documentation_url)
        def get_openapi_json():
            openapi = self.generate_openapi_json()
            with open("tesjson","w") as f:
                json.dump(openapi, f, indent=4)
            return jsonify(openapi)
    
    def create_init_template(
        self,
        title: str = "Auto Swagger",
        version: str = "1.0.0",
        description: str = "",
        servers: list = []
    ):
        template = {
            "openapi": "3.0.0",
            "info": {
                "description": description,
                "version": version,
                "title": title
            },
            "servers": [{"url": s} for s in servers],
            "paths":{},
            "components":{},
            "security":[]
        }
        return template
    
    def generate_openapi_json(self):
        for router in APIRouter._api_routers.values():
            if router._is_registered:
                for ep in router.defined_endpoints:
                    ep: EndpointDefinition
                    if ep.rule not in self.template["paths"]:
                        self.template["paths"][ep.rule] = {}
                    if ep.custom_swagger:
                        self.template["paths"][ep.rule][ep.method] = ep.custom_swagger
                        continue
                    if ep.auto_swagger:
                        self.template["paths"][ep.rule][ep.method] = {
                            "tags": ep.tags,
                            "summary": ep.summary,
                            "parameters": self.generate_parameter_schema(ep.paired_params),
                            "responses": ep.responses
                        }
                        body_schema = self.generate_request_body_schema(ep.rule.replace("/","-"), ep.paired_params)
                        if body_schema:
                            if "definitions" in body_schema:
                                definitions = body_schema.pop("definitions")
                                if not "schemas" in self.template["components"]:
                                    self.template["components"]["schemas"] = {}
                                self.template["components"]["schemas"].update(definitions)
                            self.template["paths"][ep.rule][ep.method]["requestBody"] = {
                                "content":{
                                    "application/json":{
                                        "schema": body_schema
                                    }
                                }
                            }
        return self.template
    
    def generate_parameter_sub_schema(self, key, param_object):
        schema = {
            "title": key,
            "type": self.get_schema_dtype(param_object.dtype)
        }
        if param_object.description:
            schema["description"] = param_object.description
        if param_object.default and type(param_object.default) != type(...):
                schema["default"] = param_object.default
        return schema

    def generate_parameter_schema(self, paired_params: Dict[str, ParamsType]):
        schemas = []
        for k, p in paired_params.items():
            po = p.param_object
            if type(po) in [Header, Path, Query]:
                schema = {
                    "required": po.default == ...,
                    "schema": self.generate_parameter_sub_schema(k, po),
                    "name": k,
                    "in": po._type.value
                }
                if po.description:
                    schema["description"] = po.description
                schemas.append(schema)
        return schemas
    
    def generate_request_body_schema(self, name, paired_params):
        preschema = {}
        for k, p in paired_params.items():
            po = p.param_object
            if type(po) == Body:
                preschema[k] = (po.pydantic_model, ...)
        if preschema:
            if len(preschema) == 1:
                ss = preschema[k][0]
            else:
                ss = create_model(name, **preschema)
            return ss.schema(ref_template="#/components/schemas/{model}")
    
    def get_schema_dtype(self, dtype):
        schema_data_type = {
            list: "array",
            tuple: "array",
            bool: "boolean",
            int: "integer",
            float: "number",
            str: "string",
            dict: "object"
        }
        if dtype in schema_data_type:
            return schema_data_type[dtype]
        return "string"

class AutoSwagger(SwaggerGenerator):
    def __init__(
        self,
        title: str = "Auto Swagger",
        version: str = "0.0.1",
        description: str = "Auto Swagger Documentation for Flask ",
        servers: list = [],
        base_url: str = "/docs",
        json_url: str = "/openapi.json"
    ) -> None:
        super().__init__(
            title=title,
            documentation_version=version,
            documentation_description=description,
            documentation_servers=servers
        )
        self.swagger_ui = get_swaggerui_blueprint(base_url=base_url, api_url=json_url)
    
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
        
        ## register the swagger launcher
        app.register_blueprint(self.swagger_ui)