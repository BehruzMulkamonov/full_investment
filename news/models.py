from django.db import models
from django.utils.timezone import now


class News(models.Model):
    title = models.CharField(max_length=256)
    body = models.TextField()
    image = models.ImageField(upload_to='files/news/', default='default.jpg')
    date_created = models.DateTimeField(blank=True, null=True, default=None)
    
    def __str__(self):
        return self.title