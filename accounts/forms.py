from allauth.account.forms import SignupForm
from django import forms

from members.models import Member


class MemberSignupForm(SignupForm):
    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()

        try:
            member = Member.objects.get(email__iexact=email)
        except Member.DoesNotExist:
            raise forms.ValidationError(
                "Diese E-Mail ist nicht im Mitgliederverzeichnis freigeschaltet."
            )

        if member.user_id is not None:
            raise forms.ValidationError(
                "Für diese E-Mail existiert bereits ein Account."
            )

        if not member.is_current_member:
            raise forms.ValidationError(
                "Dieses Mitglied ist nicht für den internen Bereich freigeschaltet."
            )

        self.member = member
        return email

    def save(self, request):
        user = super().save(request)

        member = self.member
        member.user = user
        member.email = user.email
        member.save(update_fields=["user", "email"])

        return user
