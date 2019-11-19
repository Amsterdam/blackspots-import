from datasets.blackspots.models import Document, Spot


def clear_models():
    Spot.objects.all().delete()
    Document.objects.all().delete()
