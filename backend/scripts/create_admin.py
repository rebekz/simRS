#!/usr/bin/env python
"""
Create admin user script.

This script creates a default admin user for the SIMRS system.
Usage: python scripts/create_admin.py
"""
import asyncio
import sys
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import getpass
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import AsyncSessionLocal, engine
from app.models.user import User, UserRole
from app.schemas.user import UserCreate
from app.crud.user import create_user, get_user_by_username


async def create_admin_user(
    username: str,
    email: str,
    full_name: str,
    password: str
) -> User:
    """Create an admin user"""
    async with AsyncSessionLocal() as db:
        # Check if user already exists
        existing_user = await get_user_by_username(db, username)
        if existing_user:
            print(f"Error: User '{username}' already exists!")
            return None

        # Create admin user
        user_in = UserCreate(
            username=username,
            email=email,
            full_name=full_name,
            password=password,
            role=UserRole.ADMIN,
            is_active=True
        )

        user = await create_user(db, user_in)
        user.is_superuser = True
        await db.commit()
        await db.refresh(user)

        return user


async def main():
    """Main function to create admin user"""
    print("=== SIMRS Admin User Creation ===\n")

    # Get user input
    username = input("Enter admin username [default: admin]: ").strip() or "admin"
    email = input("Enter admin email [default: admin@simrs.local]: ").strip() or "admin@simrs.local"
    full_name = input("Enter admin full name [default: System Administrator]: ").strip() or "System Administrator"

    # Get password
    password = getpass.getpass("Enter admin password [default: admin123]: ")
    if not password:
        password = "admin123"
        print("Using default password: admin123")

    password_confirm = getpass.getpass("Confirm password: ")
    if password != password_confirm:
        print("Error: Passwords do not match!")
        sys.exit(1)

    # Create user
    print(f"\nCreating admin user: {username}")
    try:
        user = await create_admin_user(
            username=username,
            email=email,
            full_name=full_name,
            password=password
        )

        if user:
            print(f"\n✓ Admin user created successfully!")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Full Name: {user.full_name}")
            print(f"  Role: {user.role.value}")
            print(f"\nPlease change the default password after first login!")
        else:
            print("\n✗ Failed to create admin user")
            sys.exit(1)

    except Exception as e:
        print(f"\n✗ Error creating admin user: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
