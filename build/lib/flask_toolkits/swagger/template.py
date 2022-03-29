import enum
from typing import Any, List, Optional

class SchemaObjectType(enum.Enum):
    array = "array"
    boolean = "boolean"
    integer = "integer"
    number = "number"
    json_object = "object"
    string = "string"

def PathTemplate(
        callbacks: Optional[dict] = None,
        deprecated: bool = False,
        description: Optional[str] = "",
        externalDocs: Optional[dict] = "",
        operationId: Optional[str] = "",
        parameters: Optional[List[Any]] = [],
        requestBody: Optional[Any] = None,
        responses: Optional[dict] = {},
        security: Optional[List[Any]] = [],
        servers: Optional[dict] = {},
        summary: Optional[str] = "",
        tags: Optional[List[Any]] = [],
    ):
        blank_template = {}
        if callbacks:
            blank_template["callbacks"] = callbacks
        if deprecated:
            blank_template["deprecated"] = deprecated
        if description:
            blank_template["description"] = description
        if externalDocs:
            blank_template["externalDocs"] = externalDocs
        if operationId:
            blank_template["operationId"] = operationId
        if parameters:
            blank_template["parameters"] = parameters
        if requestBody:
            blank_template["requestBody"] = requestBody
        if responses:
            blank_template["responses"] = responses
        else:
            blank_template["responses"] = {
                200: {
                    "content": {
                        "application/json": {
                            "schema": {}
                        }
                    },
                    "description": "Successful Response"
                    }
            }
        if security:
            blank_template["security"] = security
        if servers:
            blank_template["servers"] = servers
        if summary:
            blank_template["summary"] = summary
        if tags:
            blank_template["tags"] = tags
        # return {path:{method: blank_template}}
        return blank_template

def JSONSchemaTemplate(
    additionalProperties: Optional[bool] = None,
    allOf: Optional[list] = None,
    anyOf: Optional[list] = None,
    default: Optional[Any] = None,
    deprecated: Optional[bool] = None,
    description: Optional[str] = None,
    discriminator: Optional[dict] = None,
    enum: Optional[List[dict]] = None,
    example: Optional[dict] = None,
    exclusiveMaximum: Optional[bool] = None,
    exclusiveMinimum: Optional[bool] = None,
    externalDocs: Optional[dict] = None,
    format_: Optional[Any] = None,
    items: Optional[dict] = None,
    maximum: Optional[int] = None,
    maxItems: Optional[int] = None,
    maxLength: Optional[int] = None,
    maxProperties: Optional[int] = None,
    minimum: Optional[int] = None,
    minItems: Optional[int] = None,
    minLength: Optional[int] = None,
    minProperties: Optional[int] = None,
    multipleOf: Optional[int] = None,
    not_: Optional[dict] = None,
    nullable: Optional[bool] = None,
    oneOf: Optional[list] = None,
    pattern: Optional[Any] = None,
    properties: Optional[dict] = None,
    readOnly: Optional[bool] = None,
    required: Optional[list] = None,
    title: Optional[str] = None,
    type_: SchemaObjectType = SchemaObjectType.string,
    uniqueItems: Optional[bool] = None,
    writeOnly: Optional[bool] = None,
    xml: Optional[dict] = None,
):
    blank_template = {}
    if additionalProperties:
        blank_template["additionalProperties"] = additionalProperties
    if allOf:
        blank_template["allOf"] = allOf
    if anyOf:
        blank_template["anyOf"] = anyOf
    if default:
        blank_template["default"] = default
    if deprecated:
        blank_template["deprecated"] = deprecated
    if description:
        blank_template["description"] = description
    if discriminator:
        blank_template["discriminator"] = discriminator
    if enum:
        blank_template["enum"] = enum
    if example:
        blank_template["example"] = example
    if exclusiveMaximum:
        blank_template["exclusiveMaximum"] = exclusiveMaximum
    if exclusiveMinimum:
        blank_template["exclusiveMinimum"] = exclusiveMinimum
    if externalDocs:
        blank_template["externalDocs"] = externalDocs
    if format_:
        blank_template["format"] = format_
    if items:
        blank_template["items"] = items
    if maximum:
        blank_template["maximum"] = maximum
    if maxItems:
        blank_template["maxItems"] = maxItems
    if maxLength:
        blank_template["maxLength"] = maxLength
    if maxProperties:
        blank_template["maxProperties"] = maxProperties
    if minimum:
        blank_template["minimum"] = minimum
    if minItems:
        blank_template["minItems"] = minItems
    if minLength:
        blank_template["minLength"] = minLength
    if minProperties:
        blank_template["minProperties"] = minProperties
    if multipleOf:
        blank_template["multipleOf"] = multipleOf
    if not_:
        blank_template["_not"] = not_
    if nullable:
        blank_template["nullable"] = nullable
    if oneOf:
        blank_template["oneOf"] = oneOf
    if pattern:
        blank_template["pattern"] = pattern
    if properties:
        blank_template["properties"] = properties
    if readOnly:
        blank_template["readOnly"] = readOnly
    if required:
        blank_template["required"] = required
    if title:
        blank_template["title"] = title
    if type_:
        blank_template["type"] = type_.value
    if uniqueItems:
        blank_template["uniqueItems"] = uniqueItems
    if writeOnly:
        blank_template["writeOnly"] = writeOnly
    if xml:
        blank_template["xml"] = xml
    return blank_template