from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import ValidationError

import src.config as config

from src import responses
from src.routes import records


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
        content=jsonable_encoder(responses.build_response(errors=errors)),
        status_code=400,
    )


app.include_router(records.ProjectsRoute())
