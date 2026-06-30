# Documents Archive

Internal document archive for Protokolle and Statuten. Members can browse Sitzungsprotokolle (AV, AC, DaC, CC) and Vereinsdokumente (Satzung, Vereinsordnung, Beschlussbuch, Fuxenfibel) and view them as PDFs in the browser.

> **Django port** of [documents-archive-nextjs](https://github.com/Sephiri/documents-archive-nextjs).

## Tech Stack

| Technology | Description |
|---|---|
| [Django 6](https://www.djangoproject.com) | Python web framework |
| [PostgreSQL](https://www.postgresql.org) | Database (`psycopg`) |
| [Tailwind CSS](https://tailwindcss.com) | Utility-first CSS (via CDN) |
| [Alpine.js](https://alpinejs.dev) | Lightweight JS for interactivity |
| `python-dotenv` | `.env` file support |

## UI Layout

**Protokolle view** (sidebar + list + PDF viewer):

```
┌────────────────────┬─────────────────────────────┬──────────────────────────────┐
│ Hauptmenü          │ Protokoll-Liste             │ PDF-Viewer                   │
│                    │                             │                              │
│ Protokolle         │ AC-Protokolle               │ 2. AC 14.11.2023.pdf         │
│   AV-Protokolle    │ [Suche...]  [Filter ▼]      │                              │
│ > AC-Protokolle    │                             │ ┌──────────────────────────┐ │
│   DaC-Protokolle   │ 1. AC 02.11.2020  WS20/21   │ │                          │ │
│   CC-Protokolle    │ 2. AC 16.11.2020  WS20/21   │ │        PDF               │ │
│                    │ ...                         │ │                          │ │
│ Statuten           │                             │ └──────────────────────────┘ │
└────────────────────┴─────────────────────────────┴──────────────────────────────┘
```

## Project Structure

```
├── config/                  # Django project settings
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
├── archive/                 # Main Django app
│   ├── models.py            # Document model (maps to existing `documents` table)
│   ├── views.py             # Login, Protokolle, Statuten, file-serve views
│   ├── urls.py              # URL routing
│   ├── utils.py             # Formatting helpers (semester, date, file size)
│   └── admin.py             # Django admin registration
├── templates/
│   ├── base.html            # Root HTML shell
│   ├── login.html           # Login/register page
│   └── archive/
│       ├── base_intern.html # Sidebar layout for authenticated area
│       ├── protokolle.html  # Document list + PDF viewer (Alpine.js)
│       └── statuten.html    # Single-document PDF viewer
└── manage.py
```

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

ARCHIVE_ROOT=
```

| Variable | Description |
|---|---|
| `DJANGO_SECRET_KEY` | Django secret key (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `DEBUG` | `True` for development, `False` in production |
| `ALLOWED_HOSTS` | Comma-separated list of allowed hostnames |
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port (default: `5432`) |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `DB_NAME` | Database name |
| `ARCHIVE_ROOT` | Absolute path to the directory where PDF files are stored |

## Local Development

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env        # then fill in the values

python manage.py migrate    # creates Django auth tables (documents table already exists)
python manage.py createsuperuser
python manage.py runserver
```

The app runs at [http://localhost:8000](http://localhost:8000).

## Authentication

- **Login**: Django built-in auth. Username = email address.
- **Register**: creates an inactive user (`is_active=False`). An admin must activate the account at `/admin/`.
- **Admin panel**: `/admin/` (after `createsuperuser`).

## Database Notes

The `Document` model uses `managed = False` — Django reads the existing `documents` table without creating or migrating it. Only Django's own auth/session tables are managed via migrations.
