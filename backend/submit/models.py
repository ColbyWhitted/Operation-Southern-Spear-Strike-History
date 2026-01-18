from django.db import models
from dashboard.models import Strike

class Submission(models.Model):
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    source_url = models.URLField()
    new_strike = models.BooleanField(default=False)
    new_strike_date = models.DateField(null=True, blank=True)
    existing_strike = models.ForeignKey(Strike, null=True, blank=True, on_delete=models.SET_NULL)
    approved = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.description} - {self.pk}"
    
    class Meta:
        ordering = ['-submitted_at']