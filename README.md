# Flask Toolkits
<!-- [![Downloads](https://static.pepy.tech/personalized-badge/flask-http-middleware?period=month&units=international_system&left_color=black&right_color=green&left_text=Downloads)](https://pepy.tech/project/flask-http-middleware) -->

## Repository
- [ ] [GITHUB](https://github.com/Danangjoyoo/flask-toolkits)

## Installation
```
pip install flask-toolkits
```

## Description
Flask toolkits implements and provides several features from FastAPI like:
- automatic API documentation using `AutoSwagger` (define the function and we'll generate the openapi spec for you)
- Base HTTP Middleware (middleware with direct access to `request` and `response`)
- pydantic's validator
- Response functions that could return any type of data without worried to get error
- much more..


## Changelogs
- v0.0
    - First Upload

## AUTO SWAGGER DOCUMENTATION
define your router using `APIRouter` class, lets put it in another pyfile

`email_view.py`
```
from typing import Optional
from flask_toolkits import APIRouter, Body, Header, Query
from flask_toolkits.responses import JSONResponse


router = APIRouter("email", import_name=__name__, static_folder="/routers/email", url_prefix="/email")


@router.post("/read", tags=["Email Router])
def get_email(
    id: int = Body(...),
    name: Optional[str] = Body(...),
    token: int = Header(...),
    race: Optional[str] = Query(None)
):
    return JSONResponse({"id":id, "name": name})
```

`main.py`
```
from flask import Flask
from flask_toolkits import AutoSwagger

from email_view import router as email_router


app = Flask(__name__)

auto_swagger = AutoSwagger()

app.register_blueprint(email_router)
app.register_blueprint(auto_swagger)


if __name__ == "__main__":
    app.run()
```

then you can go to `http://localhost:5000/docs` and you will found you router is already documented

![alt text](https://github.com/Danangjoyoo/flask-toolkits/blob/main/docs/auto1.png?raw=true)