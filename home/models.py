from django.db import models

# Create your models here.
class Actions(models.Model):
    name = models.CharField(max_length=100, unique=True)
    icon = models.ImageField(max_length=100, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    active_to = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name
 
    class Meta:
        verbose_name_plural = "Actions"
        ordering = ['name']