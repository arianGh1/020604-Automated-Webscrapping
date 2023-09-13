from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class CSVHistory(models.Model):
    DATE_FORMAT = "%B %d %Y"
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    generated_files = models.TextField()
    is_running = models.BooleanField(default=False)