from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Review(models.Model):
    user_name = models.CharField(max_length=10)
    review_text = models.TextField()
    rating = models.IntegerField()
    owner = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Who wrote it; null for the old reviews (made before login existed)
