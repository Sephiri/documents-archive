# Documents Archive

Internal document archive for Protokolle and Statuten. Members can browse Sitzungsprotokolle (AV, AC, DaC, CC) and Vereinsdokumente (Satzung, Vereinsordnung, Beschlussbuch, Fuxenfibel) and view them as PDFs directly in the browser.

## Tech Stack

## UI Layout

The app uses a collapsible sidebar navigation with a content area on the right.

**Protokolle view** (sidebar + list + PDF viewer):

```
┌────────────────────┬─────────────────────────────┬──────────────────────────────┐
│ Hauptmenü          │ Protokoll-Liste             │ PDF-Viewer                   │
│                    │                             │                              │
│ Protokolle         │ AC-Protokolle               │ 2. AC 14.11.2023.pdf         │
│   AV-Protokolle    │ [Suche...]                  │                              │
│ > AC-Protokolle    │ [Jahr ▼] [Semester ▼]       │ ┌──────────────────────────┐ │
│   DaC-Protokolle   │                             │ │                          │ │
│   CC-Protokolle    │ 1. AC 02.11.2020            │ │        PDF               │ │
│                    │ 2. AC 16.11.2020            │ │                          │ │
│ Statuten           │ 3. AC 30.11.2020            │ └──────────────────────────┘ │
│   Satzung          │ ...                         │                              │
└────────────────────┴─────────────────────────────┴──────────────────────────────┘
```

**Statuten view** (sidebar + PDF viewer):

```
┌────────────────────┬──────────────────────────────────────────────┐
│ Hauptmenü          │ PDF-Viewer                                   │
│                    │                                              │
│ Protokolle         │ Satzung                                      │
│   AV-Protokolle    │ ┌──────────────────────────────────────────┐ │
│   AC-Protokolle    │ │                                          │ │
│   DaC-Protokolle   │ │                 PDF                      │ │
│   CC-Protokolle    │ │                                          │ │
│                    │ └──────────────────────────────────────────┘ │
│ Statuten           │                                              │
│ > Satzung          │                                              │
│   Vereinsordnung   │                                              │
│   Beschlussbuch    │                                              │
│   Fuxenfibel       │                                              │
└────────────────────┴──────────────────────────────────────────────┘
```

## Project Structure

```
├── app/
│   ├── api/files/[id]/          # API route: fetch a PDF file by ID
│   ├── intern/                  # Internal area (authenticated route)
│   │   ├── protokolle/[type]/   # Protokolle pages (av, ac, dac, cc)
│   │   └── statuten/[document]/  # Statuten pages
│   └── layout.tsx               # Root layout
├── components/
│   └── ui/                      # shadcn/ui components
├── hooks/                       # React hooks (e.g. use-mobile)
├── lib/                         # Server utilities, format helpers, API helpers
├── types/                       # TypeScript type definitions
└── public/                      # Static assets (Wappen, SVGs)
```

## Environment Variables

Create a `.env.local` file in the project root:

```env
DB_HOST=127.0.0.1
DB_PORT=
DB_USER=
DB_PASSWORD=
DB_NAME=
ARCHIVE_ROOT=
```

| Variable | Description |
|---|---|
| `DB_HOST` | PostgreSQL host |
| `DB_PORT` | PostgreSQL port (default: `5432`) |
| `DB_USER` | Database user |
| `DB_PASSWORD` | Database password |
| `DB_NAME` | Database name |
| `ARCHIVE_ROOT` | Absolute path to the directory where PDF files are stored |

## Local Development