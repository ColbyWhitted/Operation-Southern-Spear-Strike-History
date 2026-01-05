from django.db import models

# Create your models here.
# This model is not showing up in migrations


class Strike(models.Model):
    date = models.DateField()
    location_label = models.CharField(max_length=255)
    location_lat = models.DecimalField(max_digits=16, decimal_places=14, blank=True, null=True)
    location_lon = models.DecimalField(max_digits=16, decimal_places=14, blank=True, null=True)
    location_uncertainty_m = models.PositiveIntegerField(blank=True, null=True)
    target = models.CharField(max_length=255)
    striker = models.CharField(max_length=255)
    target_origin = models.CharField(max_length=255, null=True, blank=True)
    crew_number = models.IntegerField(null=True, blank=True)
    number_killed = models.IntegerField(null=True, blank=True)
    image_url = models.URLField(null=True, blank=True)
    video_url = models.URLField(null=True, blank=True)
    dvids_video_id = models.CharField(max_length=50, null=True, blank=True)
    target_destination = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.pk}"
    
    class Meta:
        ordering = ['-date']