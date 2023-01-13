from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import config

from routes import records


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(records.router)
