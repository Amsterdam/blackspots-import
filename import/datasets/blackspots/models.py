from django.contrib.gis.db import models


class Spot(models.Model):
    STATUS_CHOICES = (
        ('Voorbereiding', 'Voorbereiding'),
        ('Onderzoek_ontwerp', 'Onderzoek/ ontwerp'),
        ('Gereed', 'Gereed'),
        ('Geen_maatregel', 'Geen maatregel'),
        ('Uitvoering', 'Uitvoering'),
        ('Onbekend', 'Onbekend'),
    )
    SPOT_TYPES = (
        ('Blackspot', 'Blackspot'),
        ('Wegvak', 'Wegvak'),
        ('Protocol_ernstig', 'Protocol ernstig'),
        ('Protocol_dodelijk', 'Protocol dodelijk'),
        ('Risico', 'Risico'),
    )
    spot_type = models.CharField(max_length=24, choices=SPOT_TYPES)
    spot_id = models.CharField(max_length=16)
    description = models.CharField(max_length=120)
    point = models.PointField(srid=4326)
    stadsdeel = models.CharField(max_length=3)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    jaar_blackspotlijst = models.IntegerField(null=True)
    jaar_ongeval_quickscan = models.IntegerField(null=True)
    jaar_oplevering = models.IntegerField(null=True)
