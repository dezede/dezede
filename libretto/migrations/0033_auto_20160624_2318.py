# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.gis.db.models.fields
import django.core.validators
import tinymce.models


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0032_auto_20160210_0508'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='membre',
            options={'verbose_name_plural': 'membres', 'ordering': ('instrument', 'classement', 'debut'), 'verbose_name': 'membre'},
        ),
        migrations.AlterField(
            model_name='elementdeprogramme',
            name='autre',
            field=models.CharField(max_length=500, blank=True, verbose_name='autre'),
        ),
        migrations.AlterField(
            model_name='ensemble',
            name='individus',
            field=models.ManyToManyField(through='libretto.Membre', to='libretto.Individu', related_name='ensembles', verbose_name='individus'),
        ),
        migrations.AlterField(
            model_name='ensemble',
            name='siege',
            field=models.ForeignKey(to='libretto.Lieu', null=True, blank=True, related_name='ensembles', verbose_name='localisation'),
        ),
        migrations.AlterField(
            model_name='ensemble',
            name='type',
            field=models.ForeignKey(to='libretto.TypeDEnsemble', null=True, related_name='ensembles', verbose_name='type'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_date',
            field=models.DateField(db_index=True, help_text='Exemple\xa0: « 14/7/1789 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01/10/1678\xa0» pour octobre 1678) ou de l’année («\xa01/1/1830\xa0» pour 1830).', verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_date_approx',
            field=models.CharField(max_length=60, help_text='Ne remplir que si la date est approximative. Par exemple\xa0: «\xa01870\xa0», «\xa0octobre 1812\xa0», «\xa0été 1967\xa0».', blank=True, verbose_name='date (approximative)'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_heure',
            field=models.TimeField(db_index=True, null=True, help_text='Exemple\xa0: « 19:30 » pour 19h30.', blank=True, verbose_name='heure'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_heure_approx',
            field=models.CharField(max_length=30, help_text='Ne remplir que si l’heure est approximative. Par exemple\xa0: «\xa0matinée\xa0», «\xa0soirée\xa0».', blank=True, verbose_name='heure (approximative)'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_lieu_approx',
            field=models.CharField(max_length=50, help_text='Ne remplir que si le lieu (ou l’institution) est approximatif(ve).', blank=True, verbose_name='lieu (approximatif)'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_date',
            field=models.DateField(db_index=True, null=True, help_text='Exemple\xa0: « 14/7/1789 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01/10/1678\xa0» pour octobre 1678) ou de l’année («\xa01/1/1830\xa0» pour 1830).', blank=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_date_approx',
            field=models.CharField(max_length=60, help_text='Ne remplir que si la date est approximative. Par exemple\xa0: «\xa01870\xa0», «\xa0octobre 1812\xa0», «\xa0été 1967\xa0».', blank=True, verbose_name='date (approximative)'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_heure',
            field=models.TimeField(db_index=True, null=True, help_text='Exemple\xa0: « 19:30 » pour 19h30.', blank=True, verbose_name='heure'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_heure_approx',
            field=models.CharField(max_length=30, help_text='Ne remplir que si l’heure est approximative. Par exemple\xa0: «\xa0matinée\xa0», «\xa0soirée\xa0».', blank=True, verbose_name='heure (approximative)'),
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_lieu_approx',
            field=models.CharField(max_length=50, help_text='Ne remplir que si le lieu (ou l’institution) est approximatif(ve).', blank=True, verbose_name='lieu (approximatif)'),
        ),
        migrations.AlterField(
            model_name='fichier',
            name='fichier',
            field=models.FileField(upload_to='files/', verbose_name='fichier'),
        ),
        migrations.AlterField(
            model_name='fichier',
            name='folio',
            field=models.CharField(max_length=10, blank=True, verbose_name='folio'),
        ),
        migrations.AlterField(
            model_name='fichier',
            name='page',
            field=models.CharField(max_length=10, blank=True, verbose_name='page'),
        ),
        migrations.AlterField(
            model_name='genredoeuvre',
            name='parents',
            field=models.ManyToManyField(to='libretto.GenreDOeuvre', related_name='enfants', blank=True, verbose_name='parents'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='deces_date',
            field=models.DateField(db_index=True, null=True, help_text='Exemple\xa0: « 14/7/1789 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01/10/1678\xa0» pour octobre 1678) ou de l’année («\xa01/1/1830\xa0» pour 1830).', blank=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='deces_date_approx',
            field=models.CharField(max_length=60, help_text='Ne remplir que si la date est approximative. Par exemple\xa0: «\xa01870\xa0», «\xa0octobre 1812\xa0», «\xa0été 1967\xa0».', blank=True, verbose_name='date (approximative)'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='deces_lieu_approx',
            field=models.CharField(max_length=50, help_text='Ne remplir que si le lieu (ou l’institution) est approximatif(ve).', blank=True, verbose_name='lieu (approximatif)'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='designation',
            field=models.CharField(max_length=1, default='S', choices=[('S', 'Standard (nom, prénoms et pseudonyme)'), ('P', 'Pseudonyme (uniquement)'), ('L', 'Nom d’usage (uniquement)'), ('B', 'Nom de naissance (standard)'), ('F', 'Prénom(s) (uniquement)')], verbose_name='affichage'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='enfants',
            field=models.ManyToManyField(through='libretto.ParenteDIndividus', to='libretto.Individu', related_name='parents', verbose_name='enfants'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='naissance_date',
            field=models.DateField(db_index=True, null=True, help_text='Exemple\xa0: « 14/7/1789 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01/10/1678\xa0» pour octobre 1678) ou de l’année («\xa01/1/1830\xa0» pour 1830).', blank=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='naissance_date_approx',
            field=models.CharField(max_length=60, help_text='Ne remplir que si la date est approximative. Par exemple\xa0: «\xa01870\xa0», «\xa0octobre 1812\xa0», «\xa0été 1967\xa0».', blank=True, verbose_name='date (approximative)'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='naissance_lieu_approx',
            field=models.CharField(max_length=50, help_text='Ne remplir que si le lieu (ou l’institution) est approximatif(ve).', blank=True, verbose_name='lieu (approximatif)'),
        ),
        migrations.AlterField(
            model_name='lieu',
            name='geometry',
            field=django.contrib.gis.db.models.fields.GeometryField(db_index=True, srid=4326, null=True, blank=True, verbose_name='géo-positionnement'),
        ),
        migrations.AlterField(
            model_name='membre',
            name='classement',
            field=models.SmallIntegerField(default=1, verbose_name='classement'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_date',
            field=models.DateField(db_index=True, null=True, help_text='Exemple\xa0: « 14/7/1789 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01/10/1678\xa0» pour octobre 1678) ou de l’année («\xa01/1/1830\xa0» pour 1830).', blank=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_date_approx',
            field=models.CharField(max_length=60, help_text='Ne remplir que si la date est approximative. Par exemple\xa0: «\xa01870\xa0», «\xa0octobre 1812\xa0», «\xa0été 1967\xa0».', blank=True, verbose_name='date (approximative)'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_heure',
            field=models.TimeField(db_index=True, null=True, help_text='Exemple\xa0: « 19:30 » pour 19h30.', blank=True, verbose_name='heure'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_heure_approx',
            field=models.CharField(max_length=30, help_text='Ne remplir que si l’heure est approximative. Par exemple\xa0: «\xa0matinée\xa0», «\xa0soirée\xa0».', blank=True, verbose_name='heure (approximative)'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_lieu_approx',
            field=models.CharField(max_length=50, help_text='Ne remplir que si le lieu (ou l’institution) est approximatif(ve).', blank=True, verbose_name='lieu (approximatif)'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='filles',
            field=models.ManyToManyField(through='libretto.ParenteDOeuvres', to='libretto.Oeuvre', related_name='meres', blank=True, verbose_name='filles'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='opus',
            field=models.CharField(blank=True, db_index=True, max_length=6, help_text='Exemple\xa0: «\xa012\xa0» pour op.\xa012, «\xa027/3\xa0» pour op.\xa027 n°\xa03, «\xa08b\xa0» pour op.\xa08\u202fb, ou encore «\xa012-15\xa0» pour op.\xa012 à\xa015.', validators=[django.core.validators.RegexValidator('^[\\d\\w\\-/]+$', 'Vous ne pouvez saisir que des chiffres, lettres non accentuées, tiret et barre oblique, le tout sans espace.')], verbose_name='opus'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='tempo',
            field=models.CharField(db_index=True, max_length=50, help_text='Exemple\xa0: «\xa0Largo\xa0», «\xa0Presto ma non troppo\xa0», etc. Ne pas saisir d’indication métronomique.', blank=True, verbose_name='tempo'),
        ),
        migrations.AlterField(
            model_name='profession',
            name='classement',
            field=models.SmallIntegerField(db_index=True, default=1, verbose_name='classement'),
        ),
        migrations.AlterField(
            model_name='saison',
            name='debut',
            field=models.DateField(help_text='Exemple\xa0: « 14/7/1789 » pour le 14 juillet 1789.', verbose_name='début'),
        ),
        migrations.AlterField(
            model_name='source',
            name='date',
            field=models.DateField(db_index=True, null=True, help_text='Exemple\xa0: « 14/7/1789 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01/10/1678\xa0» pour octobre 1678) ou de l’année («\xa01/1/1830\xa0» pour 1830).', blank=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='source',
            name='date_approx',
            field=models.CharField(max_length=60, help_text='Ne remplir que si la date est approximative. Par exemple\xa0: «\xa01870\xa0», «\xa0octobre 1812\xa0», «\xa0été 1967\xa0».', blank=True, verbose_name='date (approximative)'),
        ),
        migrations.AlterField(
            model_name='source',
            name='ensembles',
            field=models.ManyToManyField(through='libretto.SourceEnsemble', to='libretto.Ensemble', related_name='sources', verbose_name='ensembles'),
        ),
        migrations.AlterField(
            model_name='source',
            name='evenements',
            field=models.ManyToManyField(through='libretto.SourceEvenement', to='libretto.Evenement', related_name='sources', verbose_name='événements'),
        ),
        migrations.AlterField(
            model_name='source',
            name='folio',
            field=models.CharField(max_length=10, help_text='Sans «\xa0f.\xa0». Exemple\xa0: «\xa03\xa0».', blank=True, verbose_name='folio'),
        ),
        migrations.AlterField(
            model_name='source',
            name='individus',
            field=models.ManyToManyField(through='libretto.SourceIndividu', to='libretto.Individu', related_name='sources', verbose_name='individus'),
        ),
        migrations.AlterField(
            model_name='source',
            name='legende',
            field=models.CharField(max_length=600, help_text='Recommandée pour les images.', blank=True, verbose_name='légende'),
        ),
        migrations.AlterField(
            model_name='source',
            name='lieux',
            field=models.ManyToManyField(through='libretto.SourceLieu', to='libretto.Lieu', related_name='sources', verbose_name='lieux'),
        ),
        migrations.AlterField(
            model_name='source',
            name='oeuvres',
            field=models.ManyToManyField(through='libretto.SourceOeuvre', to='libretto.Oeuvre', related_name='sources', verbose_name='œuvres'),
        ),
        migrations.AlterField(
            model_name='source',
            name='parties',
            field=models.ManyToManyField(through='libretto.SourcePartie', to='libretto.Partie', related_name='sources', verbose_name='sources'),
        ),
        migrations.AlterField(
            model_name='source',
            name='transcription',
            field=tinymce.models.HTMLField(help_text='Recopier la source ou un extrait en suivant les règles définies dans <a href="/examens/source/">le didacticiel.</a>', blank=True, verbose_name='transcription'),
        ),
        migrations.AlterField(
            model_name='source',
            name='url',
            field=models.URLField(help_text='Uniquement un permalien extérieur à Dezède.', blank=True, verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='typedecaracteristiquedeprogramme',
            name='classement',
            field=models.SmallIntegerField(default=1, verbose_name='classement'),
        ),
    ]
