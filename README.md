# Documents Archive

Django rebuild of the internal documents archive. The app uses the existing `documents` PostgreSQL table, displays protocol collections and statute documents, and streams PDF files from the archive directory.

## Tech Stack

| Technology | Description |
|---|---|
| Django | Server-rendered web app, routing, templates, tests |
| PostgreSQL | Existing metadata database |
| psycopg | PostgreSQL driver for Django |
| Django templates | Sidebar, lists, detail panels, embedded PDF viewer |

## Features

- Internal sidebar navigation for Protokolle and Statuten
- Protocol collection pages for AV, AC, DaC and CC
- Search, year filter and semester filter for protocol lists
- Single-document pages for Satzung, Vereinsordnung, Beschlussbuch and Fuxenfibel
- Secure PDF streaming through `/api/files/<id>/`
- Safe archive path handling below `ARCHIVE_ROOT`
- Unit tests for labels, filters, file path safety and core views

## Environment

Create `.env` from `.env.example`:

```env
DJANGO_SECRET_KEY=change-me
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

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

If `DB_NAME` is empty, Django falls back to SQLite so tests and `manage.py check` can run without the production database.

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
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

## Database

The `archive.Document` model maps to the existing `documents` table with `managed = False`. Django will not create or migrate this table automatically.

Expected columns:

- `id`
- `doc_type`
- `convent_type`
- `is_extraordinary`
- `convent_number`
- `version_date`
- `uploaded_at`
- `archive_path`
- `file_size_bytes`
