from django.conf import settings
from django.db import models

# Django-models, daraus kann eine Datenbanktabelle erstellt werden 
class Member(models.Model):
    class Status(models.TextChoices):
        FUCHS = "FUX", "Fux"
        DAME = "DAME", "Dame"
        HOHE_DAME = "HOHE_DAME", "Hohe Dame"

    user = models.OneToOneField( # 1-1 Relation zu CustomUser, damit jedes Mitglied genau einen Benutzer hat
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="member",
    )

    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    joined_at = models.DateField()

    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.FUCHS,
    )

    is_current_member = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"