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
    locatie_id = models.CharField(unique=True, max_length=16)
    spot_type = models.CharField(max_length=24, choices=SPOT_TYPES)
    description = models.CharField(max_length=120)
    point = models.PointField(srid=4326)
    stadsdeel = models.CharField(max_length=3)
    status = models.CharField(max_length=32, choices=STATUS_CHOICES)
    jaar_blackspotlijst = models.IntegerField(null=True)
    jaar_ongeval_quickscan = models.IntegerField(null=True)
    jaar_oplevering = models.IntegerField(null=True)

    def __str__(self):
        return f'{self.locatie_id}: {self.spot_type}'


class Document(models.Model):
    DOCUMENT_TYPE = (
        ('Ontwerp', 'Ontwerp'),
        ('Rapportage', 'Rapportage'),
    )
    type = models.CharField(max_length=16, choices=DOCUMENT_TYPE)
    filename = models.CharField(max_length=128)
    spot = models.ForeignKey(Spot, related_name='documents', on_delete=models.CASCADE)

    def __str__(self):
        return self.filename
