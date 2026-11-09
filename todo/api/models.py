from django.db import models
from django.contrib.auth.models import User


# Create your models here.
class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    completed = models.BooleanField(default=False)
    created_at = models.DateField(auto_now_add=True)  # Set once, when the todo is created
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Owner; deleting the user deletes their todos

    def __str__(self):
        return self.title
