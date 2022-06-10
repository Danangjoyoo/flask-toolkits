from pydantic import BaseModel, create_model
from typing import Any

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

json_model = create_model