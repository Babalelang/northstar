"""FastAPI dependencies for authentication/authorization. Kept separate
from services/auth_service.py so that module can stay pure stdlib (no
fastapi/sqlalchemy imports) while this one wires it into request handling.
"""

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from database.database import get_db
from models.user import User, UserRole
from services.auth_service import decode_token


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    """Reads the `Authorization: Bearer <token>` header, validates it, and
    returns the logged-in User. Raises 401 for anything that isn't a
    valid, unexpired token belonging to an active user.
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.removeprefix("Bearer ").strip()
    user_id = decode_token(token)
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session, please log in again",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = db.get(User, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not found or deactivated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """Same as get_current_user, but only lets ADMIN role through - use
    this on routes that manage other users (creating/deleting editors).
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can do that",
        )
    return current_user
