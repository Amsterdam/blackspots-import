from django.utils.translation import gettext_lazy as _

"""
Considering there is no proper way to add or modify translations for
third party apps, here we simply define all the strings we want to
add a translation for.

It ain't nice, but it works well.
"""

rest_framework_gis = [
    _("Invalid format: string or unicode input unrecognized as GeoJSON, WKT EWKT or HEXEWKB."),
    _("Unable to convert to python object: Invalid geometry pointer returned from 'OGR_G_CreateGeometryFromJson'."),
    _("Unable to convert to python object: String input unrecognized as WKT EWKT, and HEXEWKB."),
    _("Unable to convert to python object: String or unicode input unrecognized as WKT EWKT, and HEXEWKB."),
    _("Unable to convert to python object: Improper geometry input type:")
]
