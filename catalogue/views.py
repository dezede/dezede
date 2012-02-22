from django.shortcuts import render_to_response, redirect
from django.template import Context, RequestContext
from musicologie.catalogue.models import *
from musicologie.catalogue.forms import *
from collections import OrderedDict

def index_evenements(request, lieu_slug=None, annee=None, mois=None, jour=None):
    evenements = Evenement.objects
    if(lieu_slug): evenements = evenements.filter(ancrage_debut__lieu__slug=lieu_slug)
    if(annee): evenements = evenements.filter(ancrage_debut__date__year=int(annee))
    if(mois): evenements = evenements.filter(ancrage_debut__date__month=int(mois))
    if(jour): evenements = evenements.filter(ancrage_debut__date__day=int(jour))
    datadict = OrderedDict()
    for evenement in evenements.all():
        types = TypeDeSource.objects.filter(sources__evenements=evenement).distinct()
        sources_dict = {}
        for type in types:
            sources = evenement.sources.filter(type=type)
            if sources:
                sources_dict[type] = sources
        datadict[evenement] = sources_dict
    c = RequestContext(request, {'datadict': datadict})
    return render_to_response('evenements.html', c)

def detail_source(request, lieu_slug, annee, mois, jour):
    lieu = Lieu.objects.get(slug=lieu_slug)
    source = Source.objects.get(date__year=int(annee), date__month=int(mois), )
    c = RequestContext(request, {'source': source})
    return render_to_response('source.html', c)

def index_lieux(request):
    lieux = Lieu.objects.filter(parent=None)
    c = RequestContext(request, {'lieux': lieux})
    return render_to_response('lieux.html', c)

def detail_lieu(request, lieu_slug):
    lieu = Lieu.objects.get(slug=lieu_slug)
    c = RequestContext(request, {'lieu': lieu})
    return render_to_response('lieu.html', c)

def index_individus(request):
    c = RequestContext(request, {'individus': Individu.objects.all()})
    return render_to_response('individus.html', c)

def detail_individu(request, individu_slug):
    individu = Individu.objects.get(slug=individu_slug)
    c = RequestContext(request, {'individu': individu})
    return render_to_response('individu.html', c)

def detail_oeuvre(request, oeuvre_slug):
    oeuvre = Oeuvre.objects.get(slug=oeuvre_slug)
    c = RequestContext(request, {'oeuvre': oeuvre})
    return render_to_response('oeuvre.html', c)

def saisie_source(request, source_id=None):
    if source_id != None:
        source = Source.objects.get(pk=source_id)
    else:
        source = None
    if request.method == 'POST':
        form = SourceForm(request.POST, instance=source)
        if form.is_valid():
            form.save()
            return redirect('musicologie.catalogue.views.saisie_source')
    else:
        form = SourceForm(instance=source)
    c = RequestContext(request, {'form': form, 'sources': Source.objects.all(), 'source': source,})
    return render_to_response('saisie-source.html', c)

