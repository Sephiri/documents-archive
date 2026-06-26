from pathlib import Path

from django.conf import settings


def get_safe_archive_path(archive_path: str) -> Path:
    path = Path(archive_path)

    if path.is_absolute():
        raise ValueError("Absolute archive paths are not allowed")

    root_path = Path(settings.ARCHIVE_ROOT).resolve()
    full_path = (root_path / path).resolve()

    try:
        full_path.relative_to(root_path)
    except ValueError as exc:
        raise ValueError("Archive path escapes ARCHIVE_ROOT") from exc

    return full_path


def open_archive_file(archive_path: str):
    return get_safe_archive_path(archive_path).open("rb")
