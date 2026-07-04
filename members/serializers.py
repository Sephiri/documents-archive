def serialize_member(member):
    current_offices = getattr(member, "current_office_assignments", [])

    return {
        "id": member.pk,
        "first_name": member.first_name,
        "middle_names": member.middle_names,
        "last_name": member.last_name,
        "display_name": str(member),
        "email": member.email,
        "status": member.status,
        "status_display": member.get_status_display(),
        "activity_status": member.activity_status,
        "activity_status_display": member.get_activity_status_display() if member.activity_status else "",
        "joined_semester": member.joined_semester_display_short(),
        "study_program": member.study_program,
        "profession": member.profession,
        "bio": member.bio,
        "offices": [
            {
                "id": assignment.office_id,
                "name": assignment.office.name,
                "is_charge": assignment.office.is_charge,
            }
            for assignment in current_offices
        ],
        "wine_mother": {
            "id": member.wine_mother_id,
            "name": str(member.wine_mother),
        }
        if member.wine_mother_id
        else None,
    }
