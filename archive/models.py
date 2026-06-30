from django.db import models


class Document(models.Model):
    DOC_TYPE_CHOICES = [
        ("protokoll", "Protokoll"),
        ("satzung", "Satzung"),
        ("vereinsordnung", "Vereinsordnung"),
        ("beschlussbuch", "Beschlussbuch"),
        ("fuxenfibel", "Fuxenfibel"),
    ]

    CONVENT_TYPE_CHOICES = [
        ("av", "AV"),
        ("ac", "AC"),
        ("dac", "DaC"),
        ("cc", "CC"),
        ("dc", "DC"),
    ]

    doc_type = models.CharField(max_length=50, choices=DOC_TYPE_CHOICES)
    convent_type = models.CharField(max_length=10, choices=CONVENT_TYPE_CHOICES, null=True, blank=True)
    is_extraordinary = models.BooleanField(null=True, blank=True)
    convent_number = models.IntegerField(null=True, blank=True)
    version_date = models.DateField()
    uploaded_at = models.DateTimeField()
    archive_path = models.CharField(max_length=500, null=True, blank=True)
    file_size_bytes = models.BigIntegerField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = "documents"
        ordering = ["-version_date", "-convent_number"]

    def __str__(self) -> str:
        return f"{self.doc_type} #{self.pk}"
