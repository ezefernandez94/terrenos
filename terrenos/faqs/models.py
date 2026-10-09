from django.db import models

class Faq(models.Model):
    """
    Model representing a frequently asked question shown on the public site.
    Without a project it is a general question (landing page); with one, it shows on that project's page.
    Spanish is required; English and Portuguese are optional and fall back to Spanish.
    """
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='faqs',
    )
    question = models.CharField(max_length=255)
    answer = models.TextField()
    question_en = models.CharField(max_length=255, blank=True, default='')
    answer_en = models.TextField(blank=True, default='')
    question_pt = models.CharField(max_length=255, blank=True, default='')
    answer_pt = models.TextField(blank=True, default='')
    order = models.PositiveIntegerField(default=0, help_text="Las preguntas se muestran de menor a mayor.")
    is_published = models.BooleanField(default=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = "Pregunta frecuente"
        verbose_name_plural = "Preguntas frecuentes"
        ordering = ['order', 'id']

    @property
    def scope(self):
        return self.project.name if self.project else "General"
