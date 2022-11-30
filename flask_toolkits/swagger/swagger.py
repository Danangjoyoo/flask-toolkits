import json
import os
import enum
import time
from collections import defaultdict
from typing import Any, Callable, Dict, Mapping, List, Tuple, Union, Optional
from flask import Blueprint, Flask, jsonify
from flask.scaffold import _sentinel
from pydantic import BaseModel, create_model

from .flask_swagger_ui import get_swaggerui_blueprint
from ..params import ParamsType, FormType, ParamSignature, Header, Path, Query, Body, Form, FormURLEncoded, File
from ..routing import APIRouter, EndpointDefinition
from ..security import HTTPSecurityBase, HTTPScheme


class SwaggerGenerator(Blueprint):
    """Swagger Spec Generator"""
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
        documentation_servers: Optional[List[Dict[str, str]]] = [],
        additional_path: dict = {},
        additional_components: dict = {},
        additional_components_schema: dict = {}
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

        self.additional_path = additional_path
        self.additional_components = additional_components
        self.additional_components_schema = additional_components_schema

        @self.get(documentation_url)
        def get_openapi_json():
            openapi = self.generate_openapi_json()
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
            "components":{
                "schemas":{},
                "securitySchemes":{}
            },
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

                    ## custom swagger for one endpoint
                    if ep.custom_swagger:
                        self.template["paths"][ep.rule][ep.method] = ep.custom_swagger
                        continue

                    ## defining swagger if enabled
                    if ep.auto_swagger:
                        ## define path, query, header schema
                        param_schema, param_definition_schema = self.generate_parameter_schema(ep.paired_params)
                        self.template["paths"][ep.rule][ep.method] = {
                            "tags": ep.tags,
                            "summary": ep.summary,
                            "parameters": param_schema,
                            "responses": ep.responses
                        }
                        if param_definition_schema:
                            self.template["components"]["schemas"].update(param_definition_schema)

                        ## define body schema
                        if ep.method not in ["get", "delete"]:
                            body_schema = self.generate_body_json_schema(ep.rule.replace("/","-"), ep.paired_params)
                            if body_schema:
                                if "definitions" in body_schema:
                                    definitions = body_schema.pop("definitions")
                                    self.template["components"]["schemas"].update(definitions)
                                self.template["paths"][ep.rule][ep.method]["requestBody"] = {
                                    "content":{
                                        "application/json":{
                                            "schema": body_schema
                                        }
                                    }
                                }

                        ## define body form, form-urlencoded, file
                        all_forms = {
                            "x-www-form-urlencoded": [],
                            "multipart/form-data": []
                        }

                        for content_type, generate_schema in {
                            "form-data": self.generate_body_form_schema,
                            "x-www-form-urlencoded": self.generate_body_form_urlencoded_schema,
                            "multipart/form-data": self.generate_body_file_schema
                        }.items():
                            body_schemas = generate_schema(ep.rule.replace("/","-"), ep.paired_params)
                            content_type = "multipart/form-data" if content_type == "form-data" else content_type
                            all_forms[content_type].extend(body_schemas)

                        final_form_schema = {
                            "x-www-form-urlencoded": {
                                "schema": {
                                    "title": ep.rule.replace("/","-")+"__form_urlencoded",
                                    "type": "object",
                                    "properties": {}
                                }
                            },
                            "multipart/form-data": {
                                "schema": {
                                    "title": ep.rule.replace("/","-")+"__form",
                                    "type": "object",
                                    "properties": {}
                                }
                            }
                        }

                        for _key, _form in all_forms.items():
                            if _form:
                                for _subform in _form:
                                    final_form_schema[_key]["schema"]["properties"].update(_subform["properties"])
                                    if "required" in _subform["properties"]:
                                        if "required" not in final_form_schema[_key]["schema"]:
                                            final_form_schema[_key]["schema"]["required"] = []
                                        final_form_schema[_key]["schema"]["required"].extend(_subform["required"])
                            else:
                                final_form_schema.pop(_key)
                        if ep.method not in ["get", "delete"]:
                            if "requestBody" not in self.template["paths"][ep.rule][ep.method]:
                                self.template["paths"][ep.rule][ep.method]["requestBody"] = {"content":{}}
                            self.template["paths"][ep.rule][ep.method]["requestBody"]["content"].update(final_form_schema)

                        ## define security scheme
                        if ep.security:
                            self.template["paths"][ep.rule][ep.method]["security"] = [ep.security.schema]

        if self.additional_path:
            self.template["paths"].update(self.additional_path)

        if self.additional_components:
            self.template["components"] = self.additional_components

        if self.additional_components_schema:
            self.template["components"]["schemas"] = self.additional_components_schema

        if HTTPSecurityBase.all_schemes:
            self.template["components"]["securitySchemes"] = HTTPSecurityBase.all_schemes

        return self.template

    def generate_parameter_sub_schema(self, key: str, param_object: ParamsType):
        pydantic_model = create_model(
            key, **{key: (param_object.dtype, param_object)}
        )
        schema = pydantic_model.schema(ref_template="#/components/schemas/{model}")
        schema["type"] = self.get_schema_dtype(param_object.dtype)
        return schema

    def generate_parameter_schema(self, paired_params: Dict[str, ParamSignature]):
        schemas = []
        definitions = {}
        for k, p in paired_params.items():
            po = p.param_object
            k = p.param_object.alias or k
            if type(po) in [Header, Path, Query]:
                sub_schema = self.generate_parameter_sub_schema(k, po)
                schema = {
                    "name": k,
                    "in": po._type.value
                }
                if po.default == ... or isinstance(po, Path):
                    schema["required"] = True
                if po.description:
                    schema["description"] = po.description
                if po.example:
                    schema["example"] = po.example
                if po.default.__class__ not in [None.__class__, Ellipsis.__class__]:
                    schema["default"] = po.default
                if "definitions" in sub_schema:
                    definitions.update(sub_schema.pop("definitions"))
                    allof = sub_schema.pop("properties")[k]
                    schema["schema"] = {"allOf": [allof]}
                else:
                    schema["schema"] = sub_schema
                schemas.append(schema)
        return schemas, definitions

    def generate_body_json_schema(self, name: str, paired_params: Dict[str, ParamSignature]):
        preschema = {}
        lk = ""
        for k, p in paired_params.items():
            po = p.param_object
            k = p.param_object.alias or k
            if type(po) == Body:
                if po.pydantic_model:
                    if po.example:
                        preschema[k] = (po.pydantic_model, po)
                    else:
                        preschema[k] = (po.pydantic_model, po.default)
                else:
                    if po.example:
                        preschema[k] = (p._type, po)
                    else:
                        preschema[k] = (p._type, p._default)
                lk = k
        if preschema:
            if len(preschema) == 1:
                if BaseModel.__subclasscheck__(preschema[lk][0]):
                    ss = preschema[k][0]
                else:
                    ss = create_model(name, **preschema)
            else:
                ss = create_model(name, **preschema)
            return ss.schema(ref_template="#/components/schemas/{model}")

    def _generate_form_schema(
            self,
            name: str,
            paired_params: Dict[str, ParamSignature],
            params_type: FormType,
            force_type: Optional[Any] = None,
        ):
        all_forms = []
        for i, (k, p) in enumerate(paired_params.items()):
            k = p.param_object.alias or k
            if type(p.param_object) == params_type:
                ptype = force_type if force_type else p._type
                ss = create_model(
                    name+"_"+p.param_object._type.value+f"-{i}",
                    **{k: (ptype, p.param_object)}
                )
                all_forms.append(
                    ss.schema(ref_template="#/components/schemas/{model}")
                )
        return all_forms

    def generate_body_form_schema(self, name, paired_params):
        return self._generate_form_schema(name, paired_params, Form)

    def generate_body_form_urlencoded_schema(self, name, paired_params):
        return self._generate_form_schema(name, paired_params, FormURLEncoded)

    def generate_body_file_schema(self, name, paired_params):
        body_form = self._generate_form_schema(name, paired_params, File, str)
        for b in body_form:
            b["properties"][
                list(b["properties"].keys())[0]
            ]["format"] = "binary"
        return body_form

    def unite_form_schema(self, name, all_forms):
        1

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
        else:
            if dtype.__class__ == enum.EnumMeta:
                return "enum"
        return "string"

class AutoSwagger(SwaggerGenerator):
    """Swagger Generator Blueprints to allow automatic documentation for flask's view functions"""
    def __init__(
        self,
        title: str = "Auto Swagger",
        version: str = "0.0.1",
        description: str = "Auto Swagger Documentation for Flask ",
        servers: list = [],
        base_url: str = "/docs",
        json_url: str = "/openapi.json",
        additional_path: dict = {},
        additional_components: dict = {},
        additional_components_schema: dict = {}
    ) -> None:
        super().__init__(
            title=title,
            documentation_version=version,
            documentation_description=description,
            documentation_servers=servers,
            additional_path=additional_path,
            additional_components=additional_components,
            additional_components_schema=additional_components_schema
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