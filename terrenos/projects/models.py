from django.db import models

class Project(models.Model):
    """
    Model representing a project.
    """
    name = models.CharField(max_length=100, unique=True)
    ## description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    ## budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Projecto"
        verbose_name_plural = "Projectos"
        ordering = ['start_date']