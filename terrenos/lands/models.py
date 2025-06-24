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
    notes = models.TextField(blank=True, null=True)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE)
    seller = models.ForeignKey('sellers.Seller', on_delete=models.CASCADE, blank=True, null=True)
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

    def __str__(self):
        return f"{self.manual_id}{self.block}"

    class Meta:
        verbose_name = "Terreno"
        verbose_name_plural = "Terrenos"
        ordering = ['manual_id']

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