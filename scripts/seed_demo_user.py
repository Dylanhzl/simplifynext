#!/usr/bin/env python3
"""Create the demo account. Maya becomes a row, not wiring.

    python scripts/seed_demo_user.py
    python scripts/seed_demo_user.py --email you@example.com --password 'something long'

Loads `demo/maya/*` through the ordinary signup + onboarding path, so the demo
account is an account like any other. Nothing in the services special-cases it.

Safe to re-run: an existing demo user is reused rather than duplicated.
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dotenv import load_dotenv  # noqa: E402
from sqlalchemy import select  # noqa: E402

load_dotenv()

# The seed loader is gated so agents cannot reach it at runtime; this script is
# one of the two callers that legitimately can.
os.environ["CREATORLOOP_ALLOW_SEED"] = "1"

from shared.db import create_all, is_sqlite, session  # noqa: E402
from shared.models import CreatorProfile, User  # noqa: E402
from shared.seed import (  # noqa: E402
    load_maya_analytics,
    load_maya_corpus,
    load_maya_inbox,
    maya_profile_form,
)
from shared.tenant import reset_profile, set_profile  # noqa: E402
from ui_client import auth  # noqa: E402

DEFAULT_EMAIL = "demo@creatorloop.local"
DEFAULT_PASSWORD = "creatorloop-demo"


async def main(email: str, password: str, force: bool) -> int:
    if is_sqlite():
        await create_all()

    async with session() as s:
        user = await s.scalar(select(User).where(User.email == email.lower()))

    if user is None:
        user = await auth.signup(email, password, display_name="CreatorLoop Demo")
        print(f"created user   {user.email}")
    else:
        print(f"user exists    {user.email}")

    form = maya_profile_form()
    profiles = await auth.list_profiles(user.id)
    existing = next((p for p in profiles if p.handle == form["handle"]), None)

    if existing is not None and not force:
        print(f"profile exists @{existing.handle} ({existing.id})")
        print("             re-run with --force to reload its demo data")
        _summary(email, password, existing)
        return 0

    profile = existing or await auth.create_profile(user.id, form)
    print(f"profile        @{profile.handle} ({profile.id})")

    ctx = set_profile(str(profile.id))
    try:
        from pipeline_manager import db

        await db.write_memory({"wins": [], "losses": [], "next_bias": []})
        docs = await load_maya_corpus()
        mails = await load_maya_inbox()
        posts = await load_maya_analytics(median_views=profile.median_views)
    finally:
        reset_profile(ctx)

    print(f"rag documents  {docs}")
    print(f"inbox items    {mails}")
    print(f"analytics      {posts}")
    _summary(email, password, profile)
    return 0


def _summary(email: str, password: str, profile: CreatorProfile) -> None:
    print()
    print("  sign in at  http://localhost:8000/signin")
    print(f"  email       {email}")
    print(f"  password    {password}")
    print(f"  profile id  {profile.id}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--email", default=DEFAULT_EMAIL)
    parser.add_argument("--password", default=DEFAULT_PASSWORD)
    parser.add_argument(
        "--force", action="store_true", help="reload demo data into an existing profile"
    )
    args = parser.parse_args()
    raise SystemExit(asyncio.run(main(args.email, args.password, args.force)))
