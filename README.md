# Documents Archive

Django rebuild of [documents-archive-nextjs](https://github.com/Sephiri/documents-archive-nextjs). The app uses the existing `documents` PostgreSQL table, shows protocol collections and statute documents, and streams PDF files from the archive directory.

## Tech Stack

| Technology | Description |
|---|---|
| Django 6 | Server-rendered web app, routing, templates, tests |
| PostgreSQL | Existing metadata database |
| psycopg | PostgreSQL driver for Django |
| Django templates | Sidebar, lists, detail panels, embedded PDF viewer |
| Custom CSS | Next/shadcn-inspired UI without a frontend build step |

## Features

- Internal sidebar navigation for Protokolle and Statuten
- Protocol collection pages for AV, AC, DaC and CC
- Client-side search, year filter and semester filter for protocol lists
- Single-document pages for Satzung, Vereinsordnung, Beschlussbuch and Fuxenfibel
- Secure PDF streaming through `/api/files/<id>/`
- Safe archive path handling below `ARCHIVE_ROOT`
- Unit tests for labels, filters, path safety and core views

## Environment Variables

Copy `.env.example` to `.env` and fill in the values:

```env
DJANGO_SECRET_KEY=change-me-to-a-random-50-char-string
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_HOST=127.0.0.1
DB_PORT=5432
DB_USER=
DB_PASSWORD=
DB_NAME=

ARCHIVE_ROOT=/home/angel/projects/documents-archive
```

`ARCHIVE_ROOT` is the absolute local base path. If the database contains `data/archive/example.pdf`, Django reads:

```txt
ARCHIVE_ROOT/data/archive/example.pdf
```

If `DB_NAME` is empty, Django falls back to SQLite so checks and most tests can run without the production database.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py runserver
```

Open:

```txt
http://127.0.0.1:8000/intern/
```

Run checks and tests:

```bash
python manage.py check
python manage.py test
```

## Database Notes

The `Document` model uses `managed = False`, so Django reads the existing `documents` table without creating or altering it. Django migrations are only needed for Django's own auth/session/admin tables.
