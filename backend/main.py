import logging
import os

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from schemas import public
from api import standings_api
from api import admin_api
from api import teams_api
from api import players_api
from api import fixtures_api
from api import auth_api

from database.database import Base, engine

import models

logger = logging.getLogger("vuva")

# Set ENVIRONMENT=production in the deployment's env vars to lock the app
# down (hide interactive API docs, keep error responses generic). Defaults
# to "development" so local `uvicorn main:app --reload` behaves exactly as
# it always has.
ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()
IS_PRODUCTION = ENVIRONMENT == "production"

# Comma-separated list of origins allowed to call this API in production,
# e.g. "https://vuva.example.com,https://www.vuva.example.com". Falls back
# to allowing any origin in development so the static frontend (opened
# straight from disk, or from a plain dev server) keeps working exactly
# as before without needing extra setup.
_cors_origins_env = os.getenv("CORS_ALLOWED_ORIGINS", "")
ALLOWED_ORIGINS = [origin.strip() for origin in _cors_origins_env.split(",") if origin.strip()]

app = FastAPI(
    title="VUVA API",
    version="1.0.0",
    # Swagger UI / ReDoc / raw OpenAPI schema are handy in development but
    # shouldn't be exposed to the public internet in production, since they
    # hand an attacker a full map of every route, parameter, and schema.
    docs_url=None if IS_PRODUCTION else "/docs",
    redoc_url=None if IS_PRODUCTION else "/redoc",
    openapi_url=None if IS_PRODUCTION else "/openapi.json",
)

#create all the database tables
Base.metadata.create_all(bind = engine)

# the frontend is a set of static html files opened straight from disk
# or served from a plain dev server, so it's on a different origin (or
# no origin at all) from the api - without this, every fetch() call from
# script.js gets blocked by the browser before it even reaches fastapi.
#
# In production, set CORS_ALLOWED_ORIGINS to the real frontend origin(s)
# instead of relying on the "*" fallback - a wildcard origin is unnecessarily
# permissive for a deployed API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS if ALLOWED_ORIGINS else ["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Catch-all for anything that isn't an HTTPException/validation error.
    Without this, an unexpected error (bad data, a bug, a downed DB) would
    let FastAPI's default handler leak a full stack trace to the client.
    We log the real details server-side and return a generic 500 instead.
    """
    if isinstance(exc, HTTPException):
        # Shouldn't normally reach this handler (FastAPI routes HTTPException
        # to its own handler first), but if it ever does, preserve the
        # original intentional status code/detail rather than masking it.
        return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail}, headers=getattr(exc, "headers", None))

    logger.exception("Unhandled exception while processing %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again later."},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Same shape as FastAPI's default 422 handler - kept explicit so it's
    obvious this is intentionally still detailed (field-level validation
    errors are safe and useful to return, unlike internal stack traces).
    """
    return JSONResponse(status_code=422, content={"detail": exc.errors()})

# every route below is now reachable under /api/<router-prefix> - this is
# our own API surface end to end, there's no external service in the loop
app.include_router(standings_api.router, prefix="/api")
app.include_router(teams_api.router, prefix="/api")
app.include_router(players_api.router, prefix="/api")
app.include_router(fixtures_api.router, prefix="/api")
app.include_router(admin_api.router, prefix="/api")
app.include_router(public.router, prefix="/api")
app.include_router(auth_api.router, prefix="/api")


@app.get("/", tags=["Root"])
def root():
    return {
        "message": "Welcome to the VUVA API!",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health():
    return {
        "status": "ok",
    }
