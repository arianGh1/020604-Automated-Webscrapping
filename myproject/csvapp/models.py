from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class CSVHistory(models.Model):
    DATE_FORMAT = "%B %d %Y"
    start_date = models.DateField()
    end_date = models.DateField()
    generated_files = models.TextField()