from django.shortcuts import render_to_response, redirect
from django.template import Context, RequestContext
from musicologie.catalogue.models import *
from musicologie.catalogue.forms import *

def index_evenements(request, lieu_slug=None, annee=None, mois=None, jour=None):
    evenements = Evenement.objects
    if(lieu_slug): evenements = evenements.filter(lieu__slug=lieu_slug)
    if(annee): evenements = evenements.filter(date_debut__year=int(annee))
    if(mois): evenements = evenements.filter(date_debut__month=int(mois))
    if(jour): evenements = evenements.filter(date_debut__day=int(jour))
    datalist = []
    for evenement in evenements.all():
        types = TypedeSource.objects.filter(sources__evenements=evenement).distinct()
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

def saisie_source(request, source_id=None):
    if source_id != None:
        source = Source.objects.get(pk=source_id)
    else:
        source = None
    if request.method == 'POST':
        form = SourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            return redirect('/saisie/source/')
    else:
        form = SourceForm(instance=source)
    c = RequestContext(request, {'form': form, 'sources': Source.objects.all(), 'source': source,})
    return render_to_response('saisie-source.html', c)

