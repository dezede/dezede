from django.shortcuts import render_to_response
from musicologie.catalogue.models import *
from datetime import date

def index_evenements(request, lieu_slug=None, annee=None, mois=None, jour=None):
    evenements = Evenement.objects
    if(lieu_slug): evenements = evenements.filter(lieu__slug=lieu_slug)
    if(annee): evenements = evenements.filter(date__year=int(annee))
    if(mois): evenements = evenements.filter(date__month=int(mois))
    if(jour): evenements = evenements.filter(date__day=int(jour))
    datalist = []
    for evenement in evenements.all():
        types = TypedeSource.objects.filter(sources__evenement=evenement).distinct()
        datalist.append([evenement, types])
    return render_to_response('evenements.html', {'datalist': datalist})

def detail_source(request, lieu_slug, annee, mois, jour):
    lieu = Lieu.objects.get(slug=lieu_slug)
    source = Source.objects.get(date__year=int(annee), date__month=int(mois), )
    return render_to_response('source.html', {'source': source})

def index_lieux(request):
    return render_to_response('lieux.html', {'lieux': Lieu.objects.all()})

def detail_lieu(request, lieu_slug):
    lieu = Lieu.objects.get(slug=lieu_slug)
    return render_to_response('lieu.html', {'lieu': lieu})

def index_individus(request):
    return render_to_response('individus.html', {'individus': Individu.objects.all()})

def detail_individu(request, individu_slug):
    individu = Individu.objects.get(slug=individu_slug)
    return render_to_response('individu.html', {'individu': individu})

