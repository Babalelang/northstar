"""Creates the first admin account so you have a way to log in at all -
without this there's a chicken-and-egg problem, since creating editors
requires being logged in as an admin already.

Run from the backend/ folder:

    python -m scripts.seed_admin_user

Prompts for a username, email and password interactively (password
input is hidden). Safe to re-run: if the username already exists it
just tells you and exits instead of creating a duplicate.
"""

import getpass
import sys

from database.database import Base, Session_Local, engine
import models
from models.user import User, UserRole
from services.auth_service import hash_password


def main():
    Base.metadata.create_all(bind=engine)
    db = Session_Local()
    try:
        print("Create the first VUVA admin account.\n")
        first_name = input("First name: ").strip() or "Admin"
        last_name = input("Last name: ").strip() or "User"
        username = input("Username: ").strip()
        email = input("Email: ").strip()
        password = getpass.getpass("Password (min 8 chars): ")

        if not username or not email:
            print("Username and email are required.")
            sys.exit(1)
        if len(password) < 8:
            print("Password must be at least 8 characters.")
            sys.exit(1)

        if db.query(User).filter(User.username == username).first():
            print(f"A user with username '{username}' already exists - nothing to do.")
            return

        admin = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password_hash=hash_password(password),
            role=UserRole.ADMIN,
            is_active=True,
        )
        db.add(admin)
        db.commit()
        print(f"\nAdmin account '{username}' created. Log in at /admin.html.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
