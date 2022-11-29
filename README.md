# Flask Toolkits
[![Downloads](https://static.pepy.tech/personalized-badge/flask-toolkits?period=total&units=international_system&left_color=black&right_color=blue&left_text=Downloads)](https://pepy.tech/project/flask-toolkits)


## Installation
```
pip install flask-toolkits
```

## Description
Flask toolkits implements and provides several features from `FastAPI` like:
- Automatic API documentation (define the function and we'll generate the `swagger`/`openapi` spec for you)
- Passing parameters through `view`/`router` function which is unable in `Flask` before
- Easy Middleware setup
- Parameters and schema validation using `Pydantic`
- Response classes that could return any type of data without worried to get error
- much more..


## Changelogs
- v0.0
    - First Upload
- v0.1
    - Integration with [flask-http-middleware](https://pypi.org/project/flask-http-middleware)
    - [pydantic](https://pypi.org/project/pydantic) support for JSON arguments and validation
    - Multiple response type generator
    - Added `JSONResponse` class to replace `jsonify` roles in send dictionary data with encoding improvements.
- v0.2
    - Supported enumeration API documentation
    - Added support for type hint from `typing`'s generic (ex: `Optional`, `Union`, `List`)
    - Fixed input parameter validations
- v0.3
    - Support `File` and `Form` input parameters validation and automatic swagger.
    - Added constraint feature for parameters (ex: limit, max/min length, greater/less than, equals than etc)
- v0.4
    - Support `Authorization` header in openapi spec.
    - Added `Authorization` processing function for security and can be used as `login` or `auth`.
- v0.5
    - Support `add_url_rule` and `route` for endpoint definition
    - Support auto swagger for multiple methods in a single endpoints
- v0.6
    - Support `alias` on endpoint parameters (path, query, header, etc) to enable
        non-pythonic terms of parameter names

## Key Tools inside this `toolkit`
- Automatic API documentation (`swagger`/`openapi`)
- Request-Response direct HTTP middleware (`flask-http-middleware`)
- Automatic parameters validation (`pydantic`)
- Response generator (JSON, Plain Text, HTML)

## Automatic Parameters Validation
The original `Blueprints` class from `flask` can't insert most of arguments inside endpoint.
Here our `APIRouter` allows you to have arguments inside your endpoint
```
from typing import Optional
from flask_toolkits import APIRouter, Body, Header, Query
from flask_toolkits.responses import JSONResponse


router = APIRouter("email", import_name=__name__, static_folder="/routers/email", url_prefix="/email")


@router.post("/read", tags=["Email Router"])
def get_email(
    id: int,
    name: Optional[str],
):
    return JSONResponse({"id": id, "name": name})

```

## Automatic API Documentation
Here our `APIRouter` allows you to auto-documenting your endpoint through `AutoSwagger`.
Define the new router using `APIRouter` class, lets put it in another pyfile

`email_view.py`
```
from typing import Optional
from flask_toolkits import APIRouter, Body, Header, Query
from flask_toolkits.responses import JSONResponse


router = APIRouter("email", import_name=__name__, static_folder="/routers/email", url_prefix="/email")


@router.post("/read", tags=["Email Router"])
def get_email(
    id: int = Body(),
    name: Optional[str] = Body(None),
    token: int = Header(),
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

---

## Supported Field Parameters
`flask-toolkits` provide multiple field parameters such as `Header`, `Query`, `Body`, `Path`, `File`, `Form`

---

## Easy Security Scheme Setup and Documentation
`flask-toolkits` helps you to define your security scheme for authorization easier than before. In advance this also give you automated documentation.

### Basic Usage
lets assume you have your own bearer security schema. You just have to create a new instance of `HTTPBearerSecurity()` to enable automatic documentation on it.
```
from flask import request
from flask_toolkits import APIRouter
from flask_toolkits.security import HTTPBearerSecurity

router = APIRouter("api", __name__)

@router.get("/home", security=HTTPBearerSecurity())
def home(message: str):
    if my_security_scheme(request):
        return JSONResponse({"message": message})
    return JSONResponse({"message": "invalid authorization"})
```

this is how it looks like
![alt text](https://github.com/Danangjoyoo/flask-toolkits/blob/main/docs/auth0.png?raw=true)

on you clicked it
![alt text](https://github.com/Danangjoyoo/flask-toolkits/blob/main/docs/auth1.png?raw=true)

### Define your own security scheme
If you want to define your own security scheme you can follow below guidance
```
from flask import request
from flask_toolkits import APIRouter
from flask_toolkits.security import HTTPBearerSecurity

class JWTBearer(HTTPBearerSecurity):
    def __init__(self):
        super().__init__()

    def __call__(self, req):
        data = self.get_authorization_data(req)
        if data != "abcdefghij":
            raise Exception("This is not good")
        return req

router = APIRouter("api", __name__)

@router.get("/home", security=JWTBearer())
def home(message: str):
    if my_security_scheme(request):
        return JSONResponse({"message": message})
    return JSONResponse({"message": "invalid authorization"})

```
Overriding `__call__` method inside the subclass would define your security schema for the routers that are using your security scheme

---

## Define to all endpoints in a router
Just pass it to `APIRouter` and all its endpoint will use that security scheme!
```
router_with_bearer = APIRouter("api", __name__, security=JWTBearer())
```
but don't worries! You can also override it by just defining in the router decorator!
```
@router_with_bearer.get("/home", security=AnotherBearerSecurity())
def home():
    return {"message": "hello"}
```

---

## Parameter Alias
In case you have non-pythonic terms with unicode character (-, +, _, =) for your paramter names, you can apply the `alias` into the parameters easily
```
@app.get("/test-alias")
def test_alias(
    apikey: str = Header(alias="x-api-key")
):
    return JSONResponse({"apikey": apikey})
```
here you will also have your swagger is defined with that `alias`
![alt text](https://github.com/Danangjoyoo/flask-toolkits/blob/main/docs/alias1.png?raw=true)


---

## Multiple HTTP Methods in a single endpoint
`add_url_rule` and `route` method for `Flask`'s App or `Blueprints` object are now supported. This also allows you to have multiple HTTP methods in a single endpoint function
```
@app.route("/test-multiple-method", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def go_multi_method(
    name: str = Body()
):
    return JSONResponse({"result": name})
```
Here you will get `null` if you hit it using `GET` but you'll get the value on you hit with other methods that support `Body`. You won't loose your validation since it only applied for methods that support that kind of params.

---

## Request-Response direct HTTP middleware
```
import time
from flask import Flask
from flask_toolkits.middleware import MiddlewareManager, BaseHTTPMiddleware

app = Flask(__name__)

class MetricsMiddleware(BaseHTTPMiddleware):
    def __init__(self):
        super().__init__()

    def dispatch(self, request, call_next):
        t0 = time.time()
        response = call_next(request)
        response_time = time.time()-t0
        response.headers.add("response_time", response_time)
        return response

app.wsgi_app = MiddlewareManager(app)
app.wsgi_app.add_middleware(MetricsMiddleware)

@app.get("/health")
def health():
    return {"message":"I'm healthy"}
```