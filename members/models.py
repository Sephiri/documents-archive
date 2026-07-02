from django.conf import settings
from django.db import models


class Member(models.Model):
    class Status(models.TextChoices):
        FUX = "FUX", "Fux"
        DAME = "DAME", "Dame"
        HOHE_DAME = "HOHE_DAME", "Hohe Dame"

    class ActivityStatus(models.TextChoices):
        AKTIV = "AKTIV", "Aktiv"
        INAKTIV = "INAKTIV", "Inaktiv"

    user = models.OneToOneField( # 1-1 Relation zu CustomUser, damit jedes Mitglied genau einen Benutzer hat
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, # im admin panel darf das Feld leer sein
        blank=True, # in der db darf null gespeichert sein
        related_name="member",
    )

    email = models.EmailField(unique=True)

    first_name = models.CharField(max_length=150)
    middle_names = models.CharField(max_length=255, blank=True)
    last_name = models.CharField(max_length=150)

    joined_at = models.DateField()
    date_of_birth = models.DateField(blank=True, null=True)

    phone = models.CharField(max_length=50, blank=True)
    address_line = models.CharField(max_length=255, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    city = models.CharField(max_length=100, blank=True)

    study_program = models.CharField(max_length=150, blank=True)
    profession = models.CharField(max_length=150, blank=True)

    bio = models.TextField(blank=True) # bei text feldern leerer string "" statt null

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.FUX,
    )

    activity_status = models.CharField(
        max_length=20,
        choices=ActivityStatus.choices,
        blank=True,
        null=True,
    )

    wine_mother = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name="wine_daughters",
    )

    is_current_member = models.BooleanField(default=True) # darf er noch in den Bereich oder ist der member ausgetreten?

    class Meta:
        db_table = "members"

    def __str__(self):
        parts = [self.first_name, self.middle_names, self.last_name]
        return " ".join(part for part in parts if part)


class Office(models.Model):
    name = models.CharField(max_length=100, unique=True)
    is_charge = models.BooleanField(default=False)
    grants_board_rights = models.BooleanField(default=False)

    class Meta:
        db_table = "offices"

    def __str__(self):
        return self.name


class OfficeAssignment(models.Model):
    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name="office_assignments",
    )

    office = models.ForeignKey(
        Office,
        on_delete=models.CASCADE,
        related_name="assignments",
    )

    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)

    class Meta:
        db_table = "office_assignments"

    def is_current(self):
        return self.end_date is None

    def __str__(self):
        return f"{self.member} – {self.office}"