from django.db import models

# Create your models here.
# This model is not showing up in migrations


class Strike(models.Model):
    date = models.DateField()
    location = models.CharField(max_length=255)
    target = models.CharField(max_length=255)
    striker = models.CharField(max_length=255)
    target_origin = models.CharField(max_length=255)
    crew_number = models.IntegerField(null=True, blank=True)
    number_killed = models.IntegerField(null=True, blank=True)
    test = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.striker} strike on {self.target} at {self.location} on {self.date}"
    
    class Meta:
        ordering = ['-date']