from members.models import Member


def can_view_document(member, document):
    if document.version_date < member.joined_at:
        return False

    if member.status == Member.Status.FUX and document.doc_type == "protokoll":
        return False

    return True