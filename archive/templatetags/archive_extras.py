from django import template

from archive.labels import DocumentData, get_document_list_title

register = template.Library()


@register.filter
def document_title(document: DocumentData) -> str:
    return get_document_list_title(document)
