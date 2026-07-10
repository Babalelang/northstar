from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.database import Base, engine
import models
from api import admin, standings

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

# every route in api/standings.py is now reachable under /api/standings
app.include_router(standings.router, prefix="/api")
app.include_router(admin.router, prefix="/api")


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
