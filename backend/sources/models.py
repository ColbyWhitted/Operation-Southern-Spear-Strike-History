from django.db import models

class Source(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()
    last_reviewed = models.DateField(auto_now=True)


    class Type(models.TextChoices):
        PRIMARY = "PRIMARY", "Primary"
        SECONDARY = "SECONDARY", "Secondary"

    type = models.CharField(
        max_length=16,
        choices=Type.choices,
        default=Type.PRIMARY
    )


    def __str__(self):
        return f"{self.name} - {self.pk}"
    
    class Meta:
        ordering = ['-last_reviewed']
