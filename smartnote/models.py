from django.db import models
from all_data.models import MainData
from accounts.models import User


class SmartNote(models.Model):
    main_data = models.ForeignKey(MainData, on_delete=models.CASCADE, related_name='smart_notes', blank=True, null=True)
    text = models.TextField(default='')
    name = models.CharField(max_length=128, blank=True, null=True)
    custom_id = models.CharField(max_length=30, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='smart_notes', blank=True, null=True)
    create_date_note = models.DateTimeField(null=True, blank=True)


