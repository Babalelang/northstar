import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./vuvadb.sqlite3"

# pool_pre_ping: before handing out a pooled connection, SQLAlchemy runs a
# lightweight "SELECT 1" against it first. If Neon has already silently
# closed the connection (which it does after a period of idleness), this
# catches the dead connection and transparently opens a fresh one instead
# of letting the query blow up with "SSL connection has been closed
# unexpectedly".
#
# pool_recycle: proactively discard and replace any connection older than
# this many seconds, so we never even try to reuse one that's likely to
# have been closed on Neon's end. 280s is comfortably under Neon's ~300s
# idle timeout on pooled connections.
#
# Both are no-ops for the sqlite fallback - sqlite doesn't have this
# "server closed an idle connection" problem, so they're harmless there.
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_pre_ping=True,
    pool_recycle=280,
)

Session_Local = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    """Create a new database session for each request."""
    db = Session_Local()
    try:
        yield db
    finally:
        db.close()