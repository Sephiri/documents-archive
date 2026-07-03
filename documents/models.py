# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class Document(models.Model):
    hash = models.TextField(unique=True)
    doc_type = models.TextField()
    convent_type = models.TextField(blank=True, null=True)
    version_date = models.DateField()
    archive_path = models.TextField(blank=True, null=True)
    content_md = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    is_extraordinary = models.BooleanField(blank=True, null=True)
    convent_number = models.IntegerField(blank=True, null=True)
    uploaded_at = models.DateTimeField()
    file_size_bytes = models.BigIntegerField()

    class Meta:
        managed = False
        db_table = 'documents'
        unique_together = (('doc_type', 'convent_type', 'version_date'),)
