from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.api import standings_api
from database.database import Base, engine
import models
from backend.api import admin_api
from backend.api import teams_api
from backend.api import players_api
from backend.api import fixtures_api

app = FastAPI(    
    title = "VUVA API",
    version = "1.0.0"
)

#create all the database tables
Base.metadata.create_all(bind = engine)

# the frontend is a set of static html files opened straight from disk
# or served from a plain dev server, so it's on a different origin (or
# no origin at all) from the api - without this, every fetch() call from
# script.js gets blocked by the browser before it even reaches fastapi
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# every route below is now reachable under /api/<router-prefix> - this is
# our own API surface end to end, there's no external service in the loop
app.include_router(standings_api.router, prefix="/api")
app.include_router(teams_api.router, prefix="/api")
app.include_router(players_api.router, prefix="/api")
app.include_router(fixtures_api.router, prefix="/api")
app.include_router(admin_api.router, prefix="/api")


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
