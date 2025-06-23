from django.db import models

class PeopleToLands(models.Model):
    """
    Model representing the relationship between a person and a land plot.
    """
    person = models.ForeignKey('people.People', on_delete=models.CASCADE)
    land = models.ForeignKey('lands.Land', on_delete=models.CASCADE)
    notes = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.person} - {self.land}"

    class Meta:
        verbose_name = "Persona a Terreno"
        verbose_name_plural = "Personas a Terrenos"
        ordering = ['person', 'land']