import re
from pathlib import Path

from django.conf import settings
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.clickjacking import xframe_options_exempt

from .models import Document
from .utils import calc_semester, format_date, format_file_size, get_document_list_title


PROTOCOL_TYPES = {
    'av': 'AV-Protokolle',
    'ac': 'AC-Protokolle',
    'dac': 'DaC-Protokolle',
    'cc': 'CC-Protokolle',
}

STATUTE_TYPES = {
    'satzung': 'Satzung',
    'vereinsordnung': 'Vereinsordnung (VO)',
    'beschlussbuch': 'Beschlussbuch',
    'fuxenfibel': 'Fuxenfibel',
}


def login_view(request):
    if request.user.is_authenticated:
        return redirect('/intern/')

    context = {}

    next_url = request.POST.get('next') or request.GET.get('next', '/intern/')
    if not url_has_allowed_host_and_scheme(next_url, allowed_hosts={request.get_host()}):
        next_url = '/intern/'
    context['next'] = next_url

    if request.method == 'POST':
        form_mode = request.POST.get('form_mode', 'login')

        if form_mode == 'login':
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect(next_url)
            context['error'] = 'Ungültige E-Mail-Adresse oder Passwort.'

        elif form_mode == 'register':
            User = get_user_model()
            email = request.POST.get('email', '').strip()
            password = request.POST.get('password', '')
            password_confirm = request.POST.get('password_confirm', '')

            if not re.match(r'\S+@\S+\.\S+', email):
                context['register_error'] = 'Ungültige E-Mail-Adresse.'
            elif not re.match(r'^(?=.*[A-Z])(?=.*[^A-Za-z0-9]).{8,}$', password):
                context['register_error'] = (
                    'Passwort muss mindestens 8 Zeichen, einen Großbuchstaben '
                    'und ein Sonderzeichen enthalten.'
                )
            elif password != password_confirm:
                context['register_error'] = 'Passwörter stimmen nicht überein.'
            elif User.objects.filter(username=email).exists():
                context['register_error'] = 'Diese E-Mail-Adresse ist bereits registriert.'
            else:
                User.objects.create_user(
                    username=email, email=email, password=password, is_active=False
                )
                context['register_success'] = (
                    'Registrierung erfolgreich! Warte auf Freischaltung durch einen Administrator.'
                )

    context['initial_mode'] = (
        'register' if ('register_error' in context or 'register_success' in context) else 'login'
    )
    return render(request, 'login.html', context)


def logout_view(request):
    logout(request)
    return redirect('/')


@login_required
def intern_index(request):
    return redirect('/intern/protokolle/av/')


@login_required
def protokolle_view(request, convent_type):
    if convent_type not in PROTOCOL_TYPES:
        raise Http404

    queryset = Document.objects.filter(
        doc_type='protokoll',
        convent_type=convent_type,
    ).order_by('-version_date', '-convent_number')

    documents = [
        {
            'id': doc.id,
            'title': get_document_list_title(doc),
            'semester': calc_semester(doc.version_date),
            'version_date': doc.version_date.isoformat(),
            'upload_date': format_date(doc.uploaded_at),
            'file_size_bytes': doc.file_size_bytes,
        }
        for doc in queryset
    ]

    selected_id = None
    try:
        raw = request.GET.get('doc')
        if raw:
            selected_id = int(raw)
    except (TypeError, ValueError):
        pass

    return render(request, 'archive/protokolle.html', {
        'title': PROTOCOL_TYPES[convent_type],
        'convent_type': convent_type,
        'documents': documents,
        'selected_id': selected_id,
        'nav_main': _build_nav(request.path),
    })


@login_required
def statuten_view(request, slug):
    if slug not in STATUTE_TYPES:
        raise Http404

    document = Document.objects.filter(doc_type=slug).order_by('-version_date').first()

    doc_data = None
    if document:
        label = 'Letzte Änderung' if slug == 'fuxenfibel' else 'Beschlossen am'
        semester = calc_semester(document.version_date)
        doc_data = {
            'id': document.id,
            'title': STATUTE_TYPES[slug],
            'version_info': f'{label}: {format_date(document.version_date)} im {semester}',
            'upload_date': format_date(document.uploaded_at),
            'file_size_formatted': format_file_size(document.file_size_bytes),
            'pdf_url': f'/api/files/{document.id}/',
        }

    return render(request, 'archive/statuten.html', {
        'title': STATUTE_TYPES[slug],
        'slug': slug,
        'document': doc_data,
        'nav_main': _build_nav(request.path),
    })


@xframe_options_exempt
def file_serve_view(request, document_id):
    if not request.user.is_authenticated:
        return HttpResponse('Nicht autorisiert', status=401)

    document = get_object_or_404(Document, id=document_id)

    if not document.archive_path:
        raise Http404('Datei nicht gefunden')

    file_path = Path(settings.ARCHIVE_ROOT) / document.archive_path

    if not file_path.exists():
        raise Http404('Datei nicht gefunden')

    with open(file_path, 'rb') as f:
        content = f.read()

    title = get_document_list_title(document)
    response = HttpResponse(content, content_type='application/pdf')
    response['Content-Disposition'] = f'inline; filename="{title}.pdf"'
    return response


def _build_nav(current_path):
    return [
        {
            'title': 'Protokolle',
            'items': [
                {
                    'title': label,
                    'url': f'/intern/protokolle/{key}/',
                    'active': current_path == f'/intern/protokolle/{key}/',
                }
                for key, label in PROTOCOL_TYPES.items()
            ],
            'group_active': current_path.startswith('/intern/protokolle'),
        },
        {
            'title': 'Statuten',
            'items': [
                {
                    'title': label,
                    'url': f'/intern/statuten/{slug}/',
                    'active': current_path == f'/intern/statuten/{slug}/',
                }
                for slug, label in STATUTE_TYPES.items()
            ],
            'group_active': current_path.startswith('/intern/statuten'),
        },
    ]
