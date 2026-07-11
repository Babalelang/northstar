from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from database.database import get_db
from models import Announcement, AnnouncementStatus
from schemas.admin import AnnouncementOut

# Public-facing router — no auth, read-only, only ever returns published
# announcements. Keep this separate from api/admin_api.py, which is the
# authenticated CRUD surface and intentionally returns drafts too.
router = APIRouter(prefix="/announcements", tags=["Announcements"])


@router.get("/", response_model=list[AnnouncementOut])
def list_published_announcements(db: Session = Depends(get_db)):
    return (
        db.query(Announcement)
        .filter(Announcement.status == AnnouncementStatus.PUBLISHED)
        .filter(Announcement.deleted_at.is_(None))
        .order_by(Announcement.is_pinned.desc(), Announcement.published_at.desc())
        .all()
    )