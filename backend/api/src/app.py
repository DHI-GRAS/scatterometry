from fastapi import FastAPI, Request
from fastapi import openapi
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

import src.config as config

from src import responses
from src.routes import records


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = openapi.utils.get_openapi(
        title=app.title, version=app.version, routes=app.routes
    )

    http_methods = ["post", "get", "put", "delete"]
    # look for the error 422 and removes it
    for method in openapi_schema["paths"]:
        for m in http_methods:
            try:
                del openapi_schema["paths"][method][m]["responses"]["422"]
            except KeyError:
                pass

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(ValidationError)
async def unicorn_exception_handler(request: Request, exc: ValidationError):
    errors = [error["msg"] for error in exc.errors()]
    return JSONResponse(
        content=jsonable_encoder(responses.BasicResponse(errors=errors)),
        status_code=400,
    )


# Remove the 422 case from docs
app.openapi = custom_openapi

app.include_router(records.RecordsRoute())
