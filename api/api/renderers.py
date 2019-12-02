import csv

from rest_framework.renderers import JSONRenderer
from rest_framework_csv.misc import Echo


class StreamingCSVRenderer:

    def render(self, data, fieldnames):
        writer = csv.DictWriter(Echo(), fieldnames=fieldnames, dialect="excel")
        yield writer.writerow({name: name for name in fieldnames})

        for obj in data:
            yield writer.writerow(obj)


class GeojsonRenderer(JSONRenderer):
    """
    Simpy allows for ?format=geojson to be used to get a Json response
    """
    format = 'geojson'
