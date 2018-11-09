from django.utils.encoding import force_text
import pandas

from libretto.models import Source, Fichier


def get_row(source, oeuvre):
    individus = [a.individu for a in oeuvre.auteurs.all()]
    return {
        'permalien enregistrement': 'https://dezede.org' + source.permalien(),
        'œuvre': force_text(oeuvre),
        'permalien œuvre': 'https://dezede.org' + oeuvre.permalien(),
        'nom compositeur(s)': '; '.join([i.nom for i in individus]),
        'prénom compositeur(s)': '; '.join([i.prenoms for i in individus]),
        'naissance compositeur(s)': '; '.join(
            [i.naissance_date.isoformat() for i in individus if
             i.naissance_date]),
        'décès compositeur(s)': '; '.join(
            [i.deces_date.isoformat() for i in individus if i.deces_date]),
        'permalien compositeur(s)': '; '.join(
            ['https://dezede.org' + i.permalien() for i in individus]),
        'date d’enregistrement': source.date,
        'orchestre': '; '.join(
            [force_text(e) for e in source.ensembles.all()]),
    }


def run():
    sources = (Source.objects
               .filter(fichiers__type__in=(Fichier.AUDIO, Fichier.VIDEO))
               .distinct()
               .prefetch_related('oeuvres__auteurs__individu', 'ensembles'))

    data = []
    for source in sources:
        oeuvres = source.oeuvres.all()
        for oeuvre in oeuvres:
            data.append(get_row(source, oeuvre))

    df = pandas.DataFrame.from_records(data)
    df = df[[
        'permalien enregistrement', 'œuvre', 'permalien œuvre',
        'nom compositeur(s)', 'prénom compositeur(s)',
        'naissance compositeur(s)', 'décès compositeur(s)',
        'permalien compositeur(s)', 'date d’enregistrement', 'orchestre']]
    df.to_excel('enregistrements_dezede.xlsx', index=False)
