from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.text import slugify

## Financing plans offered publicly; always multiples of 12 installments
INSTALLMENT_PLAN_CHOICES = [(12, "12 cuotas"), (24, "24 cuotas"), (36, "36 cuotas"), (48, "48 cuotas")]


class Project(models.Model):
    """
    Model representing a project.
    Projects are never deleted (no view, admin delete disabled, PROTECT on its lands and costs);
    a closed project is marked as finished instead.
    """
    COMING_SOON = 'coming_soon'
    IN_PROGRESS = 'in_progress'
    FINISHED = 'finished'
    STATUS_CHOICES = [
        (COMING_SOON, 'Próximamente'),
        (IN_PROGRESS, 'En curso'),
        (FINISHED, 'Finalizado'),
    ]

    name = models.CharField(max_length=100, unique=True)
    ## description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    ## Finished projects are hidden from the lands and sales tables
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=IN_PROGRESS)
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

    installment_plans = ArrayField(
        models.PositiveSmallIntegerField(choices=INSTALLMENT_PLAN_CHOICES),
        blank=True,
        default=list,
        help_text="Planes de cuotas que se muestran en la web pública.",
    )

    def __str__(self):
        return self.name

    @property
    def is_finished(self):
        return self.status == self.FINISHED

    @property
    def sorted_installment_plans(self):
        return sorted(set(self.installment_plans or []))

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