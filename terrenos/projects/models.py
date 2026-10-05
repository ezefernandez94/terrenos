from django.db import models
from django.utils.text import slugify

class Project(models.Model):
    """
    Model representing a project.
    """
    name = models.CharField(max_length=100, unique=True)
    ## description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    ## budget = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    ## Public lot map: only projects with is_public=True are exposed on public pages/endpoints
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        help_text="Identificador en la URL pública (/proyectos/<slug>/). Si se deja vacío se genera desde el nombre.",
    )
    is_public = models.BooleanField(
        default=False,
        help_text="Si está activo, el proyecto y su plano se muestran en la web pública.",
    )
    ## Sanitized SVG markup, stored in the DB because uploaded media does not persist on Heroku
    map_svg = models.TextField(
        blank=True,
        default="",
        help_text="Plano interactivo (SVG ya sanitizado). Se carga desde el admin.",
    )

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = self._unique_slug()
        super().save(*args, **kwargs)

    def _unique_slug(self):
        base = slugify(self.name)[:110] or "proyecto"
        slug, n = base, 2
        while Project.objects.filter(slug=slug).exclude(pk=self.pk).exists():
            slug, n = f"{base}-{n}", n + 1
        return slug

    class Meta:
        verbose_name = "Projecto"
        verbose_name_plural = "Projectos"
        ordering = ['start_date']