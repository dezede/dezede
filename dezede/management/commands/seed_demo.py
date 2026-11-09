"""
Loads the demo data of a preview: `./manage.py seed_demo`.

Everything the command creates is owned by the `demo` account, which is how it
recognises its own records: running it again replaces them. It refuses to run,
changing nothing, when the database holds any other record, because the
sign-in below is public.

The people, places, works, events and documents are invented. The images come
from Wikimedia Commons (see `IMAGES`), or from a placeholder when a download
fails.
"""
import http.client
import urllib.parse
import urllib.request
from datetime import date, time
from decimal import Decimal
from io import BytesIO

from PIL import Image as PILImage, ImageDraw
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.management import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone
from wagtail.images.models import Image as WagtailImage
from wagtail.models import Page, Site

from accounts.models import HierarchicUser
from common.utils.file import FileAnalyzer
from correspondence.models import (
    Letter, LetterCorpus, LetterImage, LetterIndex, LetterRecipient, LetterSender)
from dezede.models import Diapositive
from dossiers.models import (
    CategorieDeDossiers, Dossier, DossierDEvenements, DossierDOeuvres)
from examens.models import Level, LevelSource
from libretto.models import (
    Auteur, ElementDeDistribution, ElementDeProgramme, Ensemble, Evenement,
    GenreDOeuvre, Individu, Lieu, Membre, NatureDeLieu, Oeuvre, Partie,
    Profession, Pupitre, Source, TypeDeSource, TypeDEnsemble)

DEMO_USERNAME = 'demo'
DEMO_PASSWORD = 'admin'
DEMO_EMAIL = 'demo@example.com'

COMMONS_URL = 'https://commons.wikimedia.org/wiki/Special:FilePath/'
USER_AGENT = 'Dezede demo data (seed_demo command; https://dezede.org)'

# Freely licensed images from Wikimedia Commons, by key. Only public domain or
# CC0 files: no attribution is required, and the sources are listed here.
IMAGES = {
    # Public domain, Commons: 18th-century engraving of a parade (théâtre).
    'parade': "A French 'parade' in the 18th century - Pougin 1887 p581.jpg",
    # Public domain, Commons: view of the Opéra in Paris, 1790–1795.
    'opera': 'Print, View of the Opera in Paris, 1790–1795 (CH 18348513).jpg',
    # Public domain, Commons: Alexis Hubert Jaillot’s plan of Paris, 1708.
    'plan': 'Alexis Hubert Jaillot, Plan de la ville cite universite et fauxbourgs de Paris, 1708 - David Rumsey.jpg',
    # CC0, Commons: harpsichord, from the Metropolitan Museum of Art.
    'harpsichord': 'Harpsichord MET DP204706a.jpg',
}
IMAGE_WIDTH = 800


def placeholder_image(text: str) -> bytes:
    image = PILImage.new('RGB', (IMAGE_WIDTH, 600), (240, 233, 218))
    ImageDraw.Draw(image).multiline_text((40, 40), text, fill=(70, 60, 50), spacing=8)
    buffer = BytesIO()
    image.save(buffer, 'PNG')
    return buffer.getvalue()


def download_images() -> dict:
    """Returns `{key: (file name, bytes)}`. A failed download gives a placeholder."""
    images = {}
    for key, commons_name in IMAGES.items():
        url = COMMONS_URL + urllib.parse.quote(commons_name) + f'?width={IMAGE_WIDTH}'
        try:
            request = urllib.request.Request(url, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(request, timeout=10) as response:
                data = response.read()
            image_format = PILImage.open(BytesIO(data)).format.lower()
        except (OSError, ValueError, http.client.HTTPException):
            data = placeholder_image(f'Image de démonstration\n({key})')
            image_format = 'png'
        extension = 'jpg' if image_format == 'jpeg' else image_format
        images[key] = (f'{key}.{extension}', data)
    return images


def owned_models():
    """Every model the command writes, in creation order.

    Deleting walks this list backwards, so each model comes after the models
    that refer to it.
    """
    return [
        NatureDeLieu, Lieu, Profession, TypeDEnsemble, Individu, Ensemble,
        GenreDOeuvre, Oeuvre, Partie, Membre, Pupitre, Auteur, Evenement,
        ElementDeProgramme, ElementDeDistribution, TypeDeSource, Source,
        CategorieDeDossiers, Dossier, Diapositive,
    ]


def find_foreign_records() -> list:
    """Returns the kinds of records that are not the demo data, with their count."""
    foreign = []
    checks = [
        ('utilisateurs', HierarchicUser.objects.exclude(username=DEMO_USERNAME)),
    ] + [
        (model.__name__, model._base_manager.exclude(owner__username=DEMO_USERNAME))
        for model in owned_models()
    ] + [
        ('pages', Page.objects.filter(depth__gt=2).exclude(owner__username=DEMO_USERNAME)),
        ('images', WagtailImage.objects.exclude(uploaded_by_user__username=DEMO_USERNAME)),
        ('niveaux de sources', LevelSource.objects.exclude(source__owner__username=DEMO_USERNAME)),
    ]
    for name, queryset in checks:
        count = queryset.count()
        if count:
            foreign.append((name, count))
    return foreign


def delete_demo_records():
    demo = HierarchicUser.objects.filter(username=DEMO_USERNAME).first()
    if demo is None:
        return
    # The letters first: they refer to people, places and images.
    for index in LetterIndex.objects.filter(owner=demo):
        index.delete()  # Also deletes the corpuses, the letters and the site rooted here.
    LevelSource.objects.filter(source__owner=demo).delete()
    WagtailImage.objects.filter(uploaded_by_user=demo).delete()
    # Files that the database does not delete with their records.
    for model, field_name in [(Source, 'fichier'), (Dossier, 'logo'), (Diapositive, 'image')]:
        for record in model._base_manager.filter(owner=demo):
            getattr(record, field_name).delete(save=False)
    for model in reversed(owned_models()):
        model._base_manager.filter(owner=demo).delete()
    demo.delete()


class Command(BaseCommand):
    help = 'Replaces the demo data with invented records, for previews and tries.'

    def handle(self, *args, **options):
        foreign = find_foreign_records()
        if foreign:
            details = ', '.join(f'{count} {name}' for name, count in foreign)
            raise CommandError(
                f'The database holds records that are not demo data ({details}). '
                f'Nothing was changed: seed_demo only runs on a database made of its own demo data.')

        images = download_images()
        with transaction.atomic():
            delete_demo_records()
            load_demo_data(images)

        self.stdout.write(self.style.SUCCESS('Demo data loaded.'))
        self.stdout.write(f'Sign in at /connexion with the username “{DEMO_USERNAME}” '
                          f'and the password “{DEMO_PASSWORD}”.')


def load_demo_data(images: dict):
    demo = HierarchicUser.objects.create_superuser(
        username=DEMO_USERNAME, email=DEMO_EMAIL, password=DEMO_PASSWORD,
        first_name='Démo', last_name='Dezède')

    # Places.
    pays, ville, institution, salle, hotel = (
        NatureDeLieu.objects.create(owner=demo, nom=nom, nom_pluriel=pluriel, referent=referent)
        for nom, pluriel, referent in [
            ('pays', 'pays', True),
            ('ville', 'villes', True),
            ('institution', 'institutions', False),
            ('salle de spectacle', 'salles de spectacle', False),
            ('hôtel particulier', 'hôtels particuliers', False),
        ])
    france = Lieu.objects.create(owner=demo, nom='France', nature=pays)
    paris = Lieu.objects.create(
        owner=demo, nom='Paris', parent=france, nature=ville,
        geometry=Point(2.3522, 48.8566, srid=4326))
    lyon = Lieu.objects.create(
        owner=demo, nom='Lyon', parent=france, nature=ville,
        geometry=Point(4.8357, 45.7640, srid=4326))
    grand_manege = Lieu.objects.create(
        owner=demo, nom='Salle du Grand Manège', parent=paris, nature=salle,
        is_institution=True, historique='<p>Salle louée par la Société des Amateurs '
                                        'pour ses concerts de carême.</p>')
    theatre = Lieu.objects.create(
        owner=demo, nom='Théâtre du Faubourg Saint-Laurent', parent=paris, nature=salle,
        is_institution=True)
    saint_aubin = Lieu.objects.create(owner=demo, nom='Hôtel de Saint-Aubin', parent=paris, nature=hotel)
    collection = Lieu.objects.create(
        owner=demo, nom='Collection particulière', parent=paris, nature=institution)
    lyon_salle = Lieu.objects.create(owner=demo, nom='Salle de l’Hôtel de ville', parent=lyon, nature=salle)

    # Professions, and the types of ensembles and works.
    musicien = Profession.objects.create(owner=demo, nom='musicien', nom_pluriel='musiciens')
    compositeur = Profession.objects.create(
        owner=demo, nom='compositeur', nom_pluriel='compositeurs',
        nom_feminin='compositrice', parent=musicien)
    violoniste = Profession.objects.create(
        owner=demo, nom='violoniste', nom_pluriel='violonistes', parent=musicien)
    claveciniste = Profession.objects.create(
        owner=demo, nom='claveciniste', nom_pluriel='clavecinistes', parent=musicien)
    chanteur = Profession.objects.create(
        owner=demo, nom='chanteur', nom_pluriel='chanteurs', nom_feminin='cantatrice',
        nom_feminin_pluriel='cantatrices', parent=musicien)
    librettiste = Profession.objects.create(
        owner=demo, nom='librettiste', nom_pluriel='librettistes')
    societe = TypeDEnsemble.objects.create(owner=demo, nom='société de concerts', nom_pluriel='sociétés de concerts')
    symphonie_genre = GenreDOeuvre.objects.create(owner=demo, nom='symphonie', nom_pluriel='symphonies')
    sonate_genre = GenreDOeuvre.objects.create(owner=demo, nom='sonate', nom_pluriel='sonates')
    opera_genre = GenreDOeuvre.objects.create(
        owner=demo, nom='opéra-comique', nom_pluriel='opéras-comiques')

    # People.
    delorme = Individu.objects.create(
        owner=demo, prenoms='Lambert', nom='Delorme', naissance_date=date(1728, 4, 12),
        naissance_lieu=lyon, deces_date=date(1789, 11, 2),
        biographie='<p>Compositeur né à Lyon et établi à Paris dès 1755. Ses symphonies '
                   'et ses opéras-comiques sont donnés dans les salles de concert de la '
                   'capitale jusqu’à la Révolution.</p>')
    vasseur = Individu.objects.create(
        owner=demo, prenoms='Adélaïde', nom='Vasseur', titre='F', naissance_date=date(1741, 9, 3),
        naissance_lieu=paris, deces_date=date(1796, 2, 20),
        biographie='<p>Cantatrice formée à Paris. Elle crée le rôle de Flore dans '
                   '<em>Le Bouquet de Flore</em>, en 1772.</p>')
    marechal = Individu.objects.create(
        owner=demo, prenoms='Étienne', nom='Maréchal', naissance_date=date(1735, 1, 8),
        naissance_lieu=paris,
        biographie='<p>Premier violon de la Société des Amateurs.</p>')
    lenoir = Individu.objects.create(
        owner=demo, prenoms='Marguerite', nom='Lenoir', titre='F', naissance_date=date(1741, 6, 25),
        naissance_lieu=paris,
        biographie='<p>Claveciniste, elle accompagne les concerts de la Société des Amateurs '
                   'et donne des soirées chez des particuliers.</p>')
    aubrac = Individu.objects.create(
        owner=demo, prenoms='Corentin', nom='Aubrac', naissance_date=date(1730, 3, 14),
        naissance_lieu=lyon, deces_date=date(1799, 5, 1),
        biographie='<p>Auteur de livrets d’opéras-comiques, il écrit les paroles du '
                   '<em>Bouquet de Flore</em>.</p>')
    delorme.professions.set([compositeur])
    vasseur.professions.set([chanteur])
    marechal.professions.set([violoniste])
    lenoir.professions.set([claveciniste])
    aubrac.professions.set([librettiste])

    ensemble = Ensemble.objects.create(
        owner=demo, nom='Société des Amateurs', type=societe, siege=grand_manege,
        debut=date(1770, 1, 1), fin=date(1780, 12, 31))

    # Instruments and roles.
    violon = Partie.objects.create(owner=demo, nom='violon', nom_pluriel='violons', type=Partie.INSTRUMENT)
    clavecin = Partie.objects.create(owner=demo, nom='clavecin', nom_pluriel='clavecins', type=Partie.INSTRUMENT)
    violoncelle = Partie.objects.create(
        owner=demo, nom='violoncelle', nom_pluriel='violoncelles', type=Partie.INSTRUMENT)
    violon.professions.set([violoniste])
    clavecin.professions.set([claveciniste])
    Membre.objects.create(owner=demo, ensemble=ensemble, individu=marechal, instrument=violon,
                          debut=date(1765, 1, 1), fin=date(1780, 12, 31))
    Membre.objects.create(owner=demo, ensemble=ensemble, individu=lenoir, instrument=clavecin,
                          debut=date(1765, 1, 1), fin=date(1780, 12, 31))

    # Works.
    symphonie = Oeuvre.objects.create(
        owner=demo, genre=symphonie_genre, numero='1', creation_date=date(1771, 3, 17),
        creation_lieu=grand_manege)
    sonate = Oeuvre.objects.create(
        owner=demo, genre=sonate_genre, titre_secondaire='pour violon et clavecin',
        creation_date=date(1771, 3, 17), creation_lieu=grand_manege)
    bouquet = Oeuvre.objects.create(
        owner=demo, prefixe_titre='Le', titre='Bouquet de Flore', genre=opera_genre,
        creation_date=date(1772, 6, 4), creation_lieu=theatre)
    Auteur.objects.create(owner=demo, oeuvre=symphonie, individu=delorme, profession=compositeur)
    Auteur.objects.create(owner=demo, oeuvre=sonate, individu=delorme, profession=compositeur)
    Auteur.objects.create(owner=demo, oeuvre=bouquet, individu=delorme, profession=compositeur)
    Auteur.objects.create(owner=demo, oeuvre=bouquet, individu=aubrac, profession=librettiste)
    flore = Partie.objects.create(
        owner=demo, nom='Flore', type=Partie.ROLE, oeuvre=bouquet, premier_interprete=vasseur)
    flore.professions.set([chanteur])
    Pupitre.objects.create(owner=demo, oeuvre=symphonie, partie=violon, quantite_min=4, quantite_max=6)
    Pupitre.objects.create(owner=demo, oeuvre=symphonie, partie=violoncelle, quantite_min=1, quantite_max=2)
    Pupitre.objects.create(owner=demo, oeuvre=sonate, partie=violon, soliste=True)
    Pupitre.objects.create(owner=demo, oeuvre=sonate, partie=clavecin, soliste=True)
    Pupitre.objects.create(owner=demo, oeuvre=bouquet, partie=flore, soliste=True)

    # Events, with their programme and distribution.
    concert = Evenement.objects.create(
        owner=demo, debut_date=date(1772, 3, 17), debut_heure=time(18, 0), debut_lieu=grand_manege,
        circonstance='Concert de carême', recette_generale=Decimal('1245.50'))
    el_symphonie = ElementDeProgramme.objects.create(owner=demo, evenement=concert, oeuvre=symphonie, position=1)
    el_sonate = ElementDeProgramme.objects.create(owner=demo, evenement=concert, oeuvre=sonate, position=2)
    el_air = ElementDeProgramme.objects.create(owner=demo, evenement=concert, oeuvre=bouquet, position=3)
    ElementDeDistribution.objects.create(owner=demo, element_de_programme=el_symphonie, ensemble=ensemble)
    ElementDeDistribution.objects.create(owner=demo, element_de_programme=el_sonate, individu=marechal, partie=violon)
    ElementDeDistribution.objects.create(owner=demo, element_de_programme=el_sonate, individu=lenoir, partie=clavecin)
    ElementDeDistribution.objects.create(owner=demo, element_de_programme=el_air, individu=vasseur, profession=chanteur)

    premiere = Evenement.objects.create(
        owner=demo, debut_date=date(1772, 6, 4), debut_heure=time(20, 0), debut_lieu=theatre,
        circonstance='Création', recette_generale=Decimal('2080.00'))
    el_bouquet = ElementDeProgramme.objects.create(owner=demo, evenement=premiere, oeuvre=bouquet, position=1)
    ElementDeDistribution.objects.create(owner=demo, element_de_programme=el_bouquet, individu=vasseur, partie=flore)
    ElementDeDistribution.objects.create(owner=demo, element_de_programme=el_bouquet, ensemble=ensemble)

    soiree = Evenement.objects.create(
        owner=demo, debut_date=date(1773, 1, 12), debut_heure=time(20, 30), debut_lieu=saint_aubin,
        circonstance='Soirée privée', programme_incomplet=True)
    el_airs = ElementDeProgramme.objects.create(
        owner=demo, evenement=soiree, autre='Airs de divers auteurs', position=1)
    ElementDeDistribution.objects.create(owner=demo, element_de_programme=el_airs, individu=lenoir, profession=claveciniste)

    Evenement.objects.create(
        owner=demo, debut_date=date(1773, 2, 14), debut_lieu=theatre, relache=True, circonstance='Carême')

    # Sources, with their images.
    affiche_type = TypeDeSource.objects.create(owner=demo, nom='affiche', nom_pluriel='affiches')
    gravure_type = TypeDeSource.objects.create(owner=demo, nom='gravure', nom_pluriel='gravures')
    plan_type = TypeDeSource.objects.create(owner=demo, nom='plan', nom_pluriel='plans')
    journal_type = TypeDeSource.objects.create(owner=demo, nom='journal', nom_pluriel='journaux')

    affiche = Source(
        owner=demo, type=affiche_type, titre='Affiche du concert du 17 mars 1772',
        legende='Illustration : gravure du XVIIIe siècle.', cote='AFF 1772-03',
        lieu_conservation='Collection particulière', date=date(1772, 3, 17),
        transcription='<p>CONCERT DE CARÊME, par la Société des Amateurs, le mardi 17 mars 1772, '
                      'à six heures du soir, dans la salle du Grand Manège. On y entendra une '
                      'symphonie de M. Delorme, une sonate pour violon et clavecin, et des airs '
                      'tirés du <em>Bouquet de Flore</em>.</p>',
        type_fichier=FileAnalyzer.IMAGE)
    affiche.fichier.save(*image_file(images, 'parade'), save=False)
    affiche.save()
    affiche.evenements.set([concert])
    affiche.oeuvres.set([symphonie, bouquet])
    affiche.individus.set([vasseur, marechal])
    affiche.ensembles.set([ensemble])
    affiche.lieux.set([grand_manege])

    gravure = Source(
        owner=demo, type=gravure_type, titre='Vue de l’Opéra de Paris',
        legende='Gravure, vers 1790–1795.', cote='GRV-OPE',
        lieu_conservation='Collection particulière', type_fichier=FileAnalyzer.IMAGE)
    gravure.fichier.save(*image_file(images, 'opera'), save=False)
    gravure.save()
    gravure.lieux.set([theatre])

    plan = Source(
        owner=demo, type=plan_type, titre='Plan de Paris en 1708',
        legende='Extrait : Alexis Hubert Jaillot, 1708.', cote='PLN-1708',
        lieu_conservation='Collection particulière', type_fichier=FileAnalyzer.IMAGE)
    plan.fichier.save(*image_file(images, 'plan'), save=False)
    plan.save()
    plan.lieux.set([paris])

    annonce = Source(
        owner=demo, type=journal_type, titre='Annonce du Bouquet de Flore',
        legende='Texte de démonstration.', lieu_conservation='Collection particulière',
        transcription='<p>On donnera le jeudi 4 juin, au Théâtre du Faubourg Saint-Laurent, '
                      'la première représentation du <em>Bouquet de Flore</em>, opéra-comique '
                      'en un acte, paroles de M. Aubrac, musique de M. Delorme.</p>')
    annonce.save()
    annonce.evenements.set([premiere])
    annonce.oeuvres.set([bouquet])
    annonce.individus.set([aubrac, delorme])

    level = Level.objects.order_by('number').first()
    if level is not None:
        LevelSource.objects.create(level=level, source=affiche)

    # Dossiers.
    concerts = CategorieDeDossiers.objects.create(owner=demo, nom='Concerts et spectacles', position=1)
    repertoire = CategorieDeDossiers.objects.create(owner=demo, nom='Répertoire', position=2)
    dossier = DossierDEvenements(
        owner=demo, categorie=concerts, titre='Concerts de la rue Saint-Honoré',
        titre_court='Concerts 1771-1773', slug='concerts-rue-saint-honore', position=1,
        debut=date(1771, 1, 1), fin=date(1773, 12, 31), circonstance='Concerts de carême',
        presentation='<p>De 1771 à 1773, la Société des Amateurs donne chaque année une série '
                     'de concerts de carême dans une salle de la rue Saint-Honoré. Ce dossier '
                     'rassemble les programmes conservés, leurs distributions et les documents '
                     'qui les annoncent.</p>',
        contexte='<p>Les concerts par souscription se développent à Paris dans les années 1770, '
                 'hors des théâtres et de l’Académie royale.</p>',
        bibliographie='<p>Documents de démonstration, sans valeur historique.</p>')
    dossier.logo.save(*image_file(images, 'harpsichord'), save=False)
    dossier.save()
    dossier.editeurs_scientifiques.set([demo])
    dossier.evenements.set([concert, premiere])
    dossier.ensembles.set([ensemble])
    dossier.individus.set([marechal, lenoir, vasseur])
    dossier.lieux.set([grand_manege, theatre])
    dossier.sources.set([affiche, annonce])

    soirees = DossierDEvenements(
        owner=demo, parent=dossier, titre='Soirées privées', titre_court='Soirées privées',
        slug='soirees-privees', position=1,
        presentation='<p>Les soirées données chez des particuliers complètent la saison publique. '
                     'Leur programme n’est connu que de manière incomplète.</p>')
    soirees.save()
    soirees.editeurs_scientifiques.set([demo])
    soirees.evenements.set([soiree])
    soirees.individus.set([lenoir])

    opera_dossier = DossierDOeuvres(
        owner=demo, categorie=repertoire, titre='Lambert Delorme à l’Opéra-Comique',
        titre_court='Delorme, opéras-comiques', slug='delorme-operas-comiques', position=1,
        presentation='<p>Ce dossier présente <em>Le Bouquet de Flore</em>, opéra-comique de Lambert '
                     'Delorme sur un livret de Corentin Aubrac, et sa création en 1772.</p>')
    opera_dossier.logo.save(*image_file(images, 'opera'), save=False)
    opera_dossier.save()
    opera_dossier.editeurs_scientifiques.set([demo])
    opera_dossier.oeuvres.set([bouquet])

    # Home page slides.
    slides = [
        (bouquet, 'Le Bouquet de Flore', 'Opéra-comique de Lambert Delorme, 1772', 'opera'),
        (vasseur, 'Adélaïde Vasseur', 'Cantatrice, créatrice du rôle de Flore', 'parade'),
        (concert, 'Concert de carême', '17 mars 1772, salle du Grand Manège', 'harpsichord'),
    ]
    for position, (record, title, subtitle, key) in enumerate(slides):
        slide = Diapositive(
            owner=demo, content_type=ContentType.objects.get_for_model(record),
            related_object_id=record.pk, title=title, subtitle=subtitle, position=position,
            text_background=True, opacity=Decimal('0.6'))
        slide.image.save(*image_file(images, key), save=False)
        slide.save()

    # Correspondence. The index of letters is the root page of the site: it
    # replaces Wagtail's default welcome page, which the frontend cannot show.
    now = timezone.now()
    index = Page.get_first_root_node().add_child(instance=LetterIndex(
        owner=demo, title='Correspondance', slug='correspondance', live=True,
        first_published_at=now, last_published_at=now))
    # The hostname and port of the site build the links to its pages.
    base_url = urllib.parse.urlsplit(settings.WAGTAILADMIN_BASE_URL)
    site_values = dict(
        hostname=base_url.hostname,
        port=base_url.port or (443 if base_url.scheme == 'https' else 80),
        site_name=settings.WAGTAIL_SITE_NAME, root_page=index)
    site = Site.objects.filter(is_default_site=True).first()
    if site is None:
        Site.objects.create(is_default_site=True, **site_values)
    else:
        welcome = site.root_page
        for name, value in site_values.items():
            setattr(site, name, value)
        site.save()
        if welcome.specific_class is Page and not welcome.get_children().exists():
            welcome.delete()
    corpus = index.add_child(instance=LetterCorpus(
        owner=demo, title='Lettres de Lambert Delorme', slug='lambert-delorme', person=delorme,
        live=True, first_published_at=now, last_published_at=now))
    letters = [
        (
            'Lambert Delorme à Corentin Aubrac, 3 février 1772', 'delorme-aubrac-1772',
            date(1772, 2, 3), delorme, aubrac,
            '<p>Mon cher Aubrac,</p><p>Je vous remercie des paroles que vous m’avez envoyées. '
            'Mademoiselle Vasseur les trouve charmantes, et je compte commencer la partition '
            'dès que la répétition du carême sera achevée.</p><p>Votre tout dévoué,</p><p>Delorme</p>',
        ),
        (
            'Adélaïde Vasseur à Lambert Delorme, 5 juin 1772', 'vasseur-delorme-1772',
            date(1772, 6, 5), vasseur, delorme,
            '<p>Monsieur,</p><p>La salle était pleine hier, et le public a redemandé l’air de Flore. '
            'Je vous en fais mon compliment et vous prie de m’envoyer la partie de chant complète '
            'avant la reprise.</p><p>Votre servante,</p><p>Vasseur</p>',
        ),
    ]
    for title, slug, writing_date, sender, recipient, transcription in letters:
        scan = WagtailImage(
            title=f'{title} (page 1)', uploaded_by_user=demo,
            file=ContentFile(placeholder_image(f'Fac-similé de démonstration\n{title}'),
                             name='lettre-page-1.png'))
        scan.save()
        corpus.add_child(instance=Letter(
            owner=demo, title=title, slug=slug, live=True,
            first_published_at=now, last_published_at=now,
            writing_date=writing_date, writing_lieu=paris,
            storage_place=collection, storage_call_number='MS 12',
            transcription=transcription, description='<p>Lettre autographe.</p>',
            senders=[LetterSender(person=sender)],
            recipients=[LetterRecipient(person=recipient)],
            letter_images=[LetterImage(image=scan, name='Page 1')],
        ))


def image_file(images: dict, key: str):
    """The arguments of `FileField.save(name, content)` for an image of `IMAGES`."""
    name, data = images[key]
    return name, ContentFile(data, name=name)
