from django.db import models

class People(models.Model):
    """
    Model representing a potential buyer.
    """
    name = models.CharField(max_length=100, blank=False, null=False)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    type = models.CharField(
        max_length=50,
        choices=[
            ('individual', 'Individual'),
            ('company', 'Company'),
            ('other', 'Other')
        ],
        default='individual'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Persona"
        verbose_name_plural = "Personas"
        ordering = ['name']
