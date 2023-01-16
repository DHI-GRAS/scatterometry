#!/bin/bash

# Run the migrations
alembic upgrade head

# Run the API
uvicorn app:app --host 0.0.0.0
