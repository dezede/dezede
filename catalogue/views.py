from django.shortcuts import render_to_response
from catalogue.models import *
from datetime import date

def index_sources(request, lieu_slug=None, annee=None, mois=None, jour=None):
    sources = Source.objects
    if(lieu_slug): sources = sources.filter(lieu__slug=lieu_slug)
    if(annee): sources = sources.filter(date__year=int(annee))
    if(mois): sources = sources.filter(date__month=int(mois))
    if(jour): sources = sources.filter(date__day=int(jour))
    return render_to_response('sources.html', {'sources': sources.all()})

def detail_source(request, lieu_slug, annee, mois, jour):
    lieu = Lieu.objects.get(slug=lieu_slug)
    source = Source.objects.get(date__year=int(annee), date__month=int(mois), )
    return render_to_response('source.html', {'source': source})

def index_lieux(request):
    return render_to_response('lieux.html', {'lieux': Lieu.objects.all()})

def detail_lieu(request, lieu_slug):
    lieu = Lieu.objects.get(slug=lieu_slug)
    return render_to_response('lieu.html', {'lieu': lieu})
