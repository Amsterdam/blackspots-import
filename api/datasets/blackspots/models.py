from django.contrib.gis.db import models
from django.utils.text import get_valid_filename
from djchoices import ChoiceItem, DjangoChoices


class Spot(models.Model):

    class StatusChoice(DjangoChoices):
        voorbereiding = ChoiceItem()
        onderzoek_ontwerp = ChoiceItem()
        gereed = ChoiceItem()
        geen_maatregel = ChoiceItem()
        uitvoering = ChoiceItem()
        onbekend = ChoiceItem()

    class SpotType(DjangoChoices):
        blackspot = ChoiceItem()
        wegvak = ChoiceItem()
        protocol_ernstig = ChoiceItem()
        protocol_dodelijk = ChoiceItem()
        risico = ChoiceItem()

    class Stadsdelen(DjangoChoices):
        Zuidoost = ChoiceItem('T')
        Centrum = ChoiceItem('A')
        Noord = ChoiceItem('N')
        Westpoort = ChoiceItem('B')
        West = ChoiceItem('E')
        Nieuw_West = ChoiceItem('F')
        Zuid = ChoiceItem('K')
        Oost = ChoiceItem('M')
        Geen = ChoiceItem('X')
        BagFout = ChoiceItem('ERR')

    locatie_id = models.CharField(unique=True, max_length=16)
    spot_type = models.CharField(max_length=24, choices=SpotType.choices)
    description = models.CharField(max_length=120)
    point = models.PointField(srid=4326)
    wegvak = models.LineStringField(srid=4326, null=True, blank=True)

    stadsdeel = models.CharField(max_length=3, choices=Stadsdelen.choices)

    status = models.CharField(
        max_length=32,
        choices=StatusChoice.choices
    )

    actiehouders = models.CharField(max_length=256)

    start_uitvoering = models.CharField(null=True, blank=True, max_length=64)
    eind_uitvoering = models.CharField(null=True, blank=True, max_length=64)
    tasks = models.TextField(null=True, blank=True)
    notes = models.TextField(null=True, blank=True)

    jaar_blackspotlijst = models.IntegerField(null=True, blank=True)
    jaar_ongeval_quickscan = models.IntegerField(null=True, blank=True)
    jaar_oplevering = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return f'{self.locatie_id}: {self.spot_type}'


class Document(models.Model):
    class DocumentType(DjangoChoices):
        Ontwerp = ChoiceItem()
        Rapportage = ChoiceItem()

    type = models.CharField(max_length=16, choices=DocumentType.choices)
    filename = models.CharField(max_length=256)
    spot = models.ForeignKey(Spot, related_name='documents', on_delete=models.CASCADE)

    def __str__(self):
        return self.filename

    def save(self, force_insert=False, force_update=False, using=None, update_fields=None):
        if self.spot and self.type and not self.filename:
            self.filename = self._generate_filename()
        super().save(force_insert, force_update, using, update_fields)

    def _generate_filename(self):
        if not self.spot_id:
            raise Exception("Spot must be set")

        doc_type = "ontwerp" if self.type == Document.DocumentType.Ontwerp else "rapportage"
        base_filename = f"{self.spot.locatie_id}_{doc_type}_{self.spot.description}.pdf"
        return get_valid_filename(base_filename)
