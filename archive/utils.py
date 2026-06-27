def calc_semester(date):
    """Return semester string for a date, e.g. 'SS24' or 'WS24/25'."""
    year = date.year
    month = date.month
    y = year % 100

    def fmt(v):
        return str(v).zfill(2)

    if 4 <= month <= 9:
        return f'SS{fmt(y)}'
    if month <= 3:
        return f'WS{fmt((year - 1) % 100)}/{fmt(y)}'
    return f'WS{fmt(y)}/{fmt((year + 1) % 100)}'


def format_date(date):
    """Return date formatted as DD.MM.YYYY."""
    return date.strftime('%d.%m.%Y')


def format_file_size(size_bytes):
    """Return human-readable file size."""
    if size_bytes is None:
        return 'Unbekannt'
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < 1024 * 1024:
        return f'{size_bytes / 1024:.1f} KB'
    return f'{size_bytes / (1024 * 1024):.1f} MB'


def get_document_list_title(doc):
    """Return display title for a document (mirrors Next.js getDocumentListTitle)."""
    if doc.doc_type != 'protokoll':
        labels = {
            'satzung': 'Satzung',
            'vereinsordnung': 'Vereinsordnung',
            'beschlussbuch': 'Beschlussbuch',
            'fuxenfibel': 'Fuxenfibel',
        }
        return labels.get(doc.doc_type, doc.doc_type)

    convent_labels = {'ac': 'AC', 'cc': 'CC', 'dac': 'DaC', 'dc': 'DC', 'av': 'AV'}
    convent_label = convent_labels.get(doc.convent_type, doc.convent_type) if doc.convent_type else None
    if convent_label and doc.is_extraordinary:
        convent_label = f'ao{convent_label}'

    parts = [
        f'{doc.convent_number}.' if doc.convent_number else None,
        convent_label,
        format_date(doc.version_date),
    ]
    return ' '.join(p for p in parts if p)
