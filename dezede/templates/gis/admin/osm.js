{% extends "gis/admin/openlayers.js" %}
{% block base_layer %}
new OpenLayers.Layer.OSM(
    "OpenStreetMap (Mapnik)", [
        'https://tile.openstreetmap.org/${z}/${x}/${y}.png'
    ]);
{% endblock %}
