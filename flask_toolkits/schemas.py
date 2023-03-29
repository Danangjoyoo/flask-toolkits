from pydantic import BaseModel, create_model
from typing import Any, Dict, Optional, Union


class BaseSchema(BaseModel):
    def __init__(__pydantic_self__, **data: Any) -> None:
        data = __pydantic_self__.filter_data(data)
        super().__init__(**data)

    @classmethod
    def get_non_exist_var_in_kwargs(cls, **kwargs):
        empty_keys = []
        keys = cls.__annotations__.keys()
        for k in keys:
            if k not in kwargs:
                empty_keys.append(k)
        return empty_keys

    @classmethod
    def filter_data(cls, datas: dict) -> dict:
        newDatas = {}
        annots = cls.__annotations__
        for key, data in datas.items():
            assert data != ..., f"Invalid value -> {key}"
            if key in annots:
                if type(annots[key]) == type:
                    if BaseModel.__subclasscheck__(annots[key]):
                        newDatas[key] = annots[key](**data)
                        continue
            newDatas[key] = data
        return newDatas

    def as_response(self):
        """
        convert schema to be a response example and schema
        """
        return response_json_example(self)

json_model = create_model


def response_json_example(
    schema_object: Optional[Union[Dict[str, Any], BaseSchema, BaseModel, BaseModel.__class__]] = {},
    example_object: Optional[Union[Dict[str, Any], BaseSchema, BaseModel]] = {},
    description: str = ""
):
    if isinstance(schema_object, (BaseModel.__class__, BaseModel, BaseSchema)):
        schema_dict = schema_object.schema()
    else:
        schema_dict = schema_object

    if not example_object:
        example_object = schema_object

    if isinstance(example_object, (BaseModel, BaseSchema)):
        example_dict = example_object.dict()
    else:
        example_dict = example_object

    response_structure = {
        "content": {"application/json": {}},
        "description": description
    }

    if schema_dict:
        response_structure["content"]["application/json"]["schema"] = schema_dict

    if example_dict:
        response_structure["content"]["application/json"]["example"] = example_dict

    return response_structure
