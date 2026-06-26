from django.db import models


class Document(models.Model):
    doc_type = models.TextField()
    convent_type = models.TextField(blank=True, null=True)
    is_extraordinary = models.BooleanField(blank=True, null=True)
    convent_number = models.IntegerField(blank=True, null=True)
    version_date = models.DateField()
    uploaded_at = models.DateTimeField()
    archive_path = models.TextField(blank=True, null=True)
    file_size_bytes = models.BigIntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = "documents"

    def __str__(self) -> str:
        return f"{self.doc_type} #{self.pk}"
