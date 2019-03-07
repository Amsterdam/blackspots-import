from datasets.blackspots.models import Spot, Document


def clear_models():
    Spot.objects.all().delete()
    Document.objects.all().delete()
