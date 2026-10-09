from django.db import models

class Land(models.Model):
    """
    Model representing a land plot.
    """
    manual_id = models.CharField(max_length=5, blank=False, null=False)
    block = models.CharField(max_length=5, blank=False, null=False)
    length = models.DecimalField(max_digits=10, decimal_places=2)
    width = models.DecimalField(max_digits=10, decimal_places=2)
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    currency = models.CharField(max_length=5, blank=False, null=False, default='USD')
    notes = models.TextField(blank=True, null=True)
    ## PROTECT: projects are never deleted, and a stray delete must not take its lands with it
    project = models.ForeignKey('projects.Project', on_delete=models.PROTECT)
    ## SET_NULL: deleting a seller only loses who sold the land, never the land itself
    seller = models.ForeignKey('sellers.Seller', on_delete=models.SET_NULL, blank=True, null=True)
    type = models.CharField(
        max_length=50,
        choices=[
            ('residential', 'Residencial'),
            ('commercial', 'Comercial'),
            ('industrial', 'Industrial'),
            ('agricultural', 'Agrícola'),
            ('recreational', 'Recreativo'),
            ('other', 'Otro')
        ],
        default='residential'
    )
    status = models.CharField(
        max_length=50,
        choices=[
            ('available', 'Disponible'),
            ('sold', 'Vendido'),
            ('reserved', 'Reservado'),
            ('under_contract', 'Bajo contrato'),
            ('not_available', 'No disponible')
        ],
        default='available'
    )
    ## Public lot map: links this land to its shape in the project's SVG
    shape_id = models.CharField(
        max_length=50,
        blank=True,
        default='',
        help_text="ID de la forma del lote en el SVG del proyecto (ej. fr8-l3). Único dentro del proyecto.",
    )
    label_x = models.FloatField(
        blank=True,
        null=True,
        help_text="Posición X de la etiqueta en coordenadas del SVG. Vacío = centro de la forma.",
    )
    label_y = models.FloatField(
        blank=True,
        null=True,
        help_text="Posición Y de la etiqueta en coordenadas del SVG. Vacío = centro de la forma.",
    )

    def __str__(self):
        return f"{self.manual_id}{self.block}"

    class Meta:
        verbose_name = "Terreno"
        verbose_name_plural = "Terrenos"
        ordering = ['manual_id']
        constraints = [
            ## Blank shape_id is allowed for any number of lands
            models.UniqueConstraint(
                fields=['project', 'shape_id'],
                condition=~models.Q(shape_id=''),
                name='uniq_land_shape_id_per_project',
            ),
        ]

    @property
    def area(self):
        """
        Calculate the area of the land.
        """
        return self.length * self.width
    
    @property
    def is_sold(self):
        """
        Check if the land is sold.
        """
        return self.status == 'sold'