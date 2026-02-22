#!/usr/bin/env python
"""
Reset migrations: drop DB and run migrate from clean 0001_initial.
Usage: python scripts/reset_migrations.py
"""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from django.conf import settings
from django.core.management import call_command

def main():
    db = settings.DATABASES["default"]
    engine = db["ENGINE"]
    name = db.get("NAME", "")

    if "sqlite" in engine:
        path = Path(name)
        if path.exists():
            path.unlink()
            print(f"Deleted {path}")
        call_command("migrate", verbosity=2)
        print("Done. Fresh migrations applied.")
    else:
        print("PostgreSQL: run these manually:")
        print("  1. DROP DATABASE your_db; CREATE DATABASE your_db;")
        print("  2. python manage.py migrate")

if __name__ == "__main__":
    main()
