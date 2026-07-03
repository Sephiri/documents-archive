from django import forms

from .models import Member


class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
            "middle_names",
            "phone",
            "address_line",
            "postal_code",
            "city",
            "study_program",
            "profession",
            "bio",
            "wine_mother",
        ]

        widgets = {
            "middle_names": forms.TextInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "address_line": forms.TextInput(attrs={"class": "form-control"}),
            "postal_code": forms.TextInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "study_program": forms.TextInput(attrs={"class": "form-control"}),
            "profession": forms.TextInput(attrs={"class": "form-control"}),
            "bio": forms.Textarea(attrs={"class": "form-control", "rows": 5}),
        }
