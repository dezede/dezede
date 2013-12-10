# coding: utf-8

from __future__ import unicode_literals
from datetime import datetime, timedelta
from random import randrange, choice
from django.db.models import Count, F
from django.template import Library
from cache_tools import cached_ugettext as ugettext
from libretto.models import (
    Evenement, Individu, Source, Oeuvre, GenreDOeuvre, Lieu, Role, Instrument)
from libretto.models.functions import capfirst


register = Library()


def html_object(tag, txt):
    return '<' + tag + '>' + txt + '</' + tag + '>'


def h3(txt):
    return html_object('h3', txt)


def h4(txt):
    return html_object('h4', txt)


def p(txt):
    return html_object('p', txt)


def read_more(obj):
    return '<a href="%s">%s</a>' % (obj.get_absolute_url(),
                                    ugettext('En savoir plus…'))


def valid_events():
    return Evenement.objects.exclude(
        programme__oeuvre__titre=''
    ).filter(
        programme__isnull=False,
        programme__oeuvre__isnull=False,
    ).distinct()


def valid_individus():
    return Individu.objects.exclude(nom='Anonyme')


def event_oeuvres(event):
    return event.oeuvres.html(auteurs=False, descr=False,
                              ancestors=False, links=False)


@register.simple_tag
def on_this_day():
    now = datetime.now()
    events = valid_events().filter(
        ancrage_debut__date__month=now.month,
        ancrage_debut__date__day=now.day)

    e = events[randrange(events.count())]

    out = h3(ugettext('Jour pour jour'))
    out += h4(ugettext('Il y a %s ans aujourd’hui')
              % (now.year - e.ancrage_debut.date.year))
    out += p(e.ancrage_debut.calc_lieu(tags=False))
    out += p(ugettext('On donnait %s') % event_oeuvres(e))
    out += read_more(e)
    return out


@register.simple_tag
def famous_event(n=10):
    """
    Affiche l’un des ``n`` événements les plus documentés.

    Or les événements les plus documentés sont généralement
    les plus remarquable.
    """

    out = h3(ugettext('L’événement'))

    data = Source.objects \
        .filter(evenements__isnull=False).values('evenements') \
        .annotate(n_sources=Count('pk')).order_by('-n_sources') \
        .values_list('evenements', 'n_sources')

    while True:
        pk, n_sources = data[randrange(n)]
        try:
            e = valid_events().get(pk=pk)
        except Evenement.DoesNotExist:
            continue
        else:
            break

    out += h4(capfirst(e.ancrage_debut.calc_moment()))
    out += h4(e.ancrage_debut.calc_lieu(tags=False))
    out += p(ugettext('On donnait %s') % event_oeuvres(e))
    out += read_more(e)
    return out


# FIXME: La requête de ce fact est cassée.
#@register.simple_tag
def traveller():
    out = h3(ugettext('Interprète voyageur'))
    Lieu.objects.values('ancrages')
    travellers = valid_individus().order_by(
        'elements_de_distribution__elements_de_programme__'
        'evenement__ancrage_debut__lieu'
    ).annotate(
        n_lieux=Count('elements_de_distribution__elements_de_programme__'
                      'evenement__ancrage_debut__lieu')).filter(n_lieux__gte=5)
    t = travellers[randrange(travellers.count())]
    out += h4(t.nom_complet(links=False))
    subject = ugettext('Elle') if t.is_feminin() else ugettext('Il')
    out += p(
        ugettext('%s a joué dans au moins %s endroits différents')
        % (subject, t.n_lieux))
    out += read_more(t)
    return out


@register.simple_tag
def prolific_author(n=20):
    out = h3(ugettext('Auteur prolifique'))

    data = Oeuvre.objects \
        .filter(auteurs__isnull=False).values('auteurs__individu') \
        .annotate(n_oeuvres=Count('pk')).order_by('-n_oeuvres') \
        .values_list('auteurs__individu', 'n_oeuvres')

    a = None
    anonyme_found = False
    while True:
        pk, n_oeuvres = data[randrange(n)]
        try:
            a = valid_individus().get(pk=pk)
        except Individu.DoesNotExist:
            # FIXME: Ici, on cherche un nouvel individu si on tombe
            #        sur Anonyme.  Il faut donc chercher parmi n+1 individus.
            if not anonyme_found:
                n += 1
                anonyme_found = True
            continue
        else:
            break

    data = a.oeuvres().values('genre').annotate(n_oeuvres=Count('genre')) \
        .order_by('-n_oeuvres').filter(n_oeuvres__gte=10)

    genres = GenreDOeuvre.objects.filter(pk__in=[d['genre'] for d in data])

    out += h4(a.nom_complet(links=False))
    subject = ugettext('Elle') if a.is_feminin() else ugettext('Il')
    if genres:
        out += p(ugettext('Genre de prédilection : %s') % genres[0])
    out += p(ugettext('%s a écrit au moins %s œuvres') % (subject, n_oeuvres))
    out += read_more(a)
    return out


# WARNING: Ce fact est peut-être erroné (voir multi-instrumentiste).
#@register.simple_tag
def transformist(n=10):
    out = h3(ugettext('« Transformiste »'))

    individu_accessor = 'pupitres__elements_de_distribution__individus'
    data = Role.objects \
        .values(individu_accessor) \
        .exclude(**{individu_accessor: None}) \
        .annotate(n_roles=Count('pk')).order_by('-n_roles') \
        .values_list(individu_accessor, 'n_roles')

    pk, n_roles = data[randrange(n)]
    t = Individu.objects.get(pk=pk)

    out += h4(t.nom_complet(links=False))
    subject = ugettext('Elle') if t.is_feminin() else ugettext('Il')
    out += p(ugettext('%s a joué au moins %s rôles différents')
             % (subject, n_roles))
    out += read_more(t)
    return out


# TODO: Ajouter les œuvres les plus représentées
#               les institutions créatrices d'œuvres
#               [les partenaires]
#               les dossiers non mis en avant
# TODO: Ajouter un booléen "remarquable" à Événement et mettre en valeur
#       les événements remarquables par un fact.


# FIXME: La requête de ce fact est cassée.
#@register.simple_tag
def multi_instrumentalist(n=10):
    out = h3(ugettext('Multi-instrumentiste'))

    individu_accessor = 'pupitres__elements_de_distribution__individus'
    data = Instrument.objects \
        .values(individu_accessor) \
        .exclude(**{individu_accessor: None}) \
        .annotate(n_instruments=Count('pk')).order_by('-n_instruments') \
        .values_list(individu_accessor, 'n_instruments')

    pk, n_instruments = data[randrange(n)]
    m = Individu.objects.get(pk=pk)

    out += h4(m.nom_complet(links=False))
    subject = ugettext('Elle') if m.is_feminin() else ugettext('Il')
    out += p(ugettext('%s a joué d’au moins %s instruments différents')
             % (subject, n_instruments))
    out += read_more(m)

    return out


# Fonctionnel mais non révélateur.
#@register.simple_tag
def centenarian():
    out = h3(ugettext('Centenaire'))

    # TODO: Faire un rapport de bug à Django.  Si on retire le `.days`,
    #       une exception inattendue est levée.
    dpy = 365.25
    an = timedelta(days=100*dpy).days
    centenarians = Individu.objects.filter(
        ancrage_deces__date__gte=F('ancrage_naissance__date') + an)
    c = centenarians[randrange(centenarians.count())]
    age = int((c.ancrage_deces.date - c.ancrage_naissance.date).days / dpy)

    out += h4(c.nom_complet(links=False))
    subject = ugettext('Elle') if c.is_feminin() else ugettext('Il')
    out += p(ugettext('%s a vécu %s ans') % (subject, age))
    out += read_more(c)
    return out


@register.simple_tag(takes_context=True)
def random_fact(context):
    used_facts = context.get('used_facts', set())
    chosen_fact = choice(list({on_this_day, famous_event,
                               prolific_author} - used_facts))
    used_facts.add(chosen_fact)
    context['used_facts'] = used_facts
    return chosen_fact()
