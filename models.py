from django.db import models
from django.contrib.auth.models import User

class JobPost(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class PredictionResult(models.Model):
    job = models.ForeignKey(JobPost, on_delete=models.CASCADE)
    prediction = models.CharField(max_length=10)
    confidence = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job.title} - {self.prediction}"