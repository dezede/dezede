from django.db import migrations, models
import libretto.models.base
import tinymce.models
import autoslug.fields
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0031_add_distribution_constraint'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='auteur',
            options={'verbose_name': 'auteur', 'ordering': ('profession', 'ensemble', 'individu'), 'verbose_name_plural': 'auteurs'},
        ),
        migrations.AlterModelOptions(
            name='etat',
            options={'verbose_name': 'état', 'ordering': ('slug',), 'verbose_name_plural': 'états'},
        ),
        migrations.AlterModelOptions(
            name='evenement',
            options={'verbose_name': 'événement', 'permissions': (('can_change_status', 'Peut changer l’état'),), 'ordering': ('debut_date', 'debut_heure', 'debut_lieu', 'debut_lieu_approx'), 'verbose_name_plural': 'événements'},
        ),
        migrations.AlterModelOptions(
            name='individu',
            options={'verbose_name': 'individu', 'permissions': (('can_change_status', 'Peut changer l’état'),), 'ordering': ('nom',), 'verbose_name_plural': 'individus'},
        ),
        migrations.AlterModelOptions(
            name='membre',
            options={'verbose_name': 'membre', 'ordering': ('instrument', 'classement', 'individu__nom'), 'verbose_name_plural': 'membres'},
        ),
        migrations.AlterField(
            model_name='auteur',
            name='oeuvre',
            field=models.ForeignKey(verbose_name='œuvre', null=True, to='libretto.Oeuvre', related_name='auteurs', blank=True, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='auteur',
            name='profession',
            field=models.ForeignKey(verbose_name='profession', to='libretto.Profession', related_name='auteurs', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='caracteristiquedeprogramme',
            name='classement',
            field=models.SmallIntegerField(default=1, verbose_name='classement', help_text='Par exemple, on peut choisir de classer les découpages par nombre d’actes.', db_index=True),
        ),
        migrations.AlterField(
            model_name='elementdedistribution',
            name='profession',
            field=models.ForeignKey(verbose_name='profession', null=True, on_delete=django.db.models.deletion.PROTECT, to='libretto.Profession', related_name='elements_de_distribution', blank=True),
        ),
        migrations.AlterField(
            model_name='elementdeprogramme',
            name='oeuvre',
            field=models.ForeignKey(verbose_name='œuvre', null=True, on_delete=django.db.models.deletion.PROTECT, to='libretto.Oeuvre', related_name='elements_de_programme', help_text='Vous pouvez croiser le titre et le nom des auteurs. Évitez les termes généraux comme «\xa0de\xa0», «\xa0la\xa0», «\xa0le\xa0», «\xa0avec\xa0».', blank=True),
        ),
        migrations.AlterField(
            model_name='ensemble',
            name='nom',
            field=models.CharField(max_length=75, verbose_name='nom', db_index=True),
        ),
        migrations.AlterField(
            model_name='ensemble',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, unique=True, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='etat',
            name='nom',
            field=models.CharField(max_length=200, verbose_name='nom', help_text='En minuscules.', unique=True),
        ),
        migrations.AlterField(
            model_name='etat',
            name='nom_pluriel',
            field=models.CharField(max_length=230, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True),
        ),
        migrations.AlterField(
            model_name='etat',
            name='public',
            field=models.BooleanField(default=True, verbose_name='publié', db_index=True),
        ),
        migrations.AlterField(
            model_name='etat',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, unique=True, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='genredoeuvre',
            name='nom',
            field=models.CharField(max_length=255, verbose_name='nom', help_text='En minuscules.', unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='genredoeuvre',
            name='nom_pluriel',
            field=models.CharField(max_length=430, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True),
        ),
        migrations.AlterField(
            model_name='genredoeuvre',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='biographie',
            field=tinymce.models.HTMLField(verbose_name='biographie', blank=True),
        ),
        migrations.AlterField(
            model_name='individu',
            name='designation',
            field=models.CharField(max_length=1, verbose_name='désignation', choices=[('S', 'Standard (nom, prénoms et pseudonyme)'), ('P', 'Pseudonyme (uniquement)'), ('L', 'Nom d’usage (uniquement)'), ('B', 'Nom de naissance (standard)'), ('F', 'Prénom(s) (uniquement)')], default='S'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='nom',
            field=models.CharField(max_length=200, verbose_name='nom d’usage', db_index=True),
        ),
        migrations.AlterField(
            model_name='individu',
            name='nom_naissance',
            field=models.CharField(max_length=200, verbose_name='nom de naissance', help_text='Ne remplir que s’il est différent du nom d’usage.', blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='individu',
            name='prenoms',
            field=models.CharField(max_length=50, verbose_name='prénoms', help_text='Exemple : « Antonio ».', blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='individu',
            name='professions',
            field=models.ManyToManyField(verbose_name='professions', related_name='individus', blank=True, to='libretto.Profession'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='pseudonyme',
            field=models.CharField(max_length=200, verbose_name='pseudonyme', blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='individu',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, unique=True, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='individu',
            name='titre',
            field=models.CharField(max_length=1, verbose_name='titre', choices=[('M', 'M.'), ('J', 'Mlle'), ('F', 'Mme')], blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='lieu',
            name='historique',
            field=tinymce.models.HTMLField(verbose_name='historique', blank=True),
        ),
        migrations.AlterField(
            model_name='lieu',
            name='nom',
            field=models.CharField(max_length=200, verbose_name='nom', db_index=True),
        ),
        migrations.AlterField(
            model_name='lieu',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, unique=True, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='naturedelieu',
            name='nom',
            field=models.CharField(max_length=255, verbose_name='nom', help_text='En minuscules.', unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='naturedelieu',
            name='nom_pluriel',
            field=models.CharField(max_length=430, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True),
        ),
        migrations.AlterField(
            model_name='naturedelieu',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_type',
            field=models.PositiveSmallIntegerField(verbose_name='type de création', null=True, choices=[(1, 'genèse (composition, écriture, etc.)'), (2, 'première mondiale'), (3, 'première édition')], blank=True),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='indeterminee',
            field=models.BooleanField(default=False, verbose_name='indéterminée', help_text='Cocher si l’œuvre n’est pas identifiable, par exemple un quatuor de Haydn, sans savoir lequel. <strong>Ne pas utiliser pour un extrait indéterminé</strong>, sélectionner plutôt dans le programme l’œuvre dont il est tiré et joindre une caractéristique le décrivant («\xa0un air\xa0», «\xa0un\xa0mouvement\xa0», etc.).'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, unique=True, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='tonalite',
            field=models.CharField(max_length=3, verbose_name='tonalité', choices=[('Cc-', 'do bémol majeur'), ('Cc0', 'do majeur'), ('Cc+', 'do dièse majeur'), ('Cd-', 'ré bémol majeur'), ('Cd0', 'ré majeur'), ('Cd+', 'ré dièse majeur'), ('Ce-', 'mi bémol majeur'), ('Ce0', 'mi majeur'), ('Ce+', 'mi dièse majeur'), ('Cf-', 'fa bémol majeur'), ('Cf0', 'fa majeur'), ('Cf+', 'fa dièse majeur'), ('Cg-', 'sol bémol majeur'), ('Cg0', 'sol majeur'), ('Cg+', 'sol dièse majeur'), ('Ca-', 'la bémol majeur'), ('Ca0', 'la majeur'), ('Ca+', 'la dièse majeur'), ('Cb-', 'si bémol majeur'), ('Cb0', 'si majeur'), ('Cb+', 'si dièse majeur'), ('Cu-', 'ut bémol majeur'), ('Cu0', 'ut majeur'), ('Cu+', 'ut dièse majeur'), ('Ac-', 'do bémol mineur'), ('Ac0', 'do mineur'), ('Ac+', 'do dièse mineur'), ('Ad-', 'ré bémol mineur'), ('Ad0', 'ré mineur'), ('Ad+', 'ré dièse mineur'), ('Ae-', 'mi bémol mineur'), ('Ae0', 'mi mineur'), ('Ae+', 'mi dièse mineur'), ('Af-', 'fa bémol mineur'), ('Af0', 'fa mineur'), ('Af+', 'fa dièse mineur'), ('Ag-', 'sol bémol mineur'), ('Ag0', 'sol mineur'), ('Ag+', 'sol dièse mineur'), ('Aa-', 'la bémol mineur'), ('Aa0', 'la mineur'), ('Aa+', 'la dièse mineur'), ('Ab-', 'si bémol mineur'), ('Ab0', 'si mineur'), ('Ab+', 'si dièse mineur'), ('Au-', 'ut bémol mineur'), ('Au0', 'ut mineur'), ('Au+', 'ut dièse mineur'), ('0c-', 'do bémol'), ('0c0', 'do'), ('0c+', 'do dièse'), ('0d-', 'ré bémol'), ('0d0', 'ré'), ('0d+', 'ré dièse'), ('0e-', 'mi bémol'), ('0e0', 'mi'), ('0e+', 'mi dièse'), ('0f-', 'fa bémol'), ('0f0', 'fa'), ('0f+', 'fa dièse'), ('0g-', 'sol bémol'), ('0g0', 'sol'), ('0g+', 'sol dièse'), ('0a-', 'la bémol'), ('0a0', 'la'), ('0a+', 'la dièse'), ('0b-', 'si bémol'), ('0b0', 'si'), ('0b+', 'si dièse'), ('0u-', 'ut bémol'), ('0u0', 'ut'), ('0u+', 'ut dièse')], blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='type_extrait',
            field=models.PositiveSmallIntegerField(verbose_name='type d’extrait', null=True, choices=[(1, 'acte'), (2, 'tableau'), (3, 'scène'), (4, 'morceau chanté'), (5, 'partie'), (6, 'livre'), (7, 'album'), (8, 'volume'), (9, 'cahier'), (10, 'ordre'), (11, 'mouvement'), (12, 'pièce de recueil')], blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='partie',
            name='classement',
            field=models.SmallIntegerField(default=1, verbose_name='classement', db_index=True),
        ),
        migrations.AlterField(
            model_name='partie',
            name='nom',
            field=models.CharField(max_length=200, verbose_name='nom', help_text='Le nom d’une partie de la partition, instrumentale ou vocale.', db_index=True),
        ),
        migrations.AlterField(
            model_name='partie',
            name='nom_pluriel',
            field=models.CharField(max_length=230, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True),
        ),
        migrations.AlterField(
            model_name='partie',
            name='oeuvre',
            field=models.ForeignKey(verbose_name='œuvre', null=True, to='libretto.Oeuvre', related_name='parties', help_text='Ne remplir que pour les rôles.', blank=True, on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='partie',
            name='professions',
            field=models.ManyToManyField(verbose_name='professions', help_text='La ou les profession(s) capable(s) de jouer ce rôle ou cet instrument.', related_name='parties', blank=True, to='libretto.Profession'),
        ),
        migrations.AlterField(
            model_name='partie',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, unique=True, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='profession',
            name='nom',
            field=models.CharField(max_length=200, verbose_name='nom', help_text='En minuscules.', unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='profession',
            name='nom_pluriel',
            field=models.CharField(max_length=230, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True),
        ),
        migrations.AlterField(
            model_name='profession',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, unique=True, always_update=True, editable=False, populate_from='get_slug'),
        ),
        migrations.AlterField(
            model_name='pupitre',
            name='oeuvre',
            field=models.ForeignKey(verbose_name='œuvre', to='libretto.Oeuvre', related_name='pupitres', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='source',
            name='legende',
            field=models.CharField(max_length=600, verbose_name='légende', blank=True),
        ),
        migrations.AlterField(
            model_name='source',
            name='type',
            field=models.ForeignKey(verbose_name='type', help_text='Exemple : « compte rendu ».', to='libretto.TypeDeSource', related_name='sources', on_delete=django.db.models.deletion.PROTECT),
        ),
        migrations.AlterField(
            model_name='sourceoeuvre',
            name='oeuvre',
            field=models.ForeignKey(verbose_name='œuvre', to='libretto.Oeuvre', related_name='sourceoeuvre_set', on_delete=models.CASCADE),
        ),
        migrations.AlterField(
            model_name='typedecaracteristiquedeprogramme',
            name='nom',
            field=models.CharField(max_length=200, verbose_name='nom', help_text='Exemple : « tonalité ».', unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='typedecaracteristiquedeprogramme',
            name='nom_pluriel',
            field=models.CharField(max_length=230, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True),
        ),
        migrations.AlterField(
            model_name='typedensemble',
            name='nom',
            field=models.CharField(max_length=30, verbose_name='nom', help_text='En minuscules.'),
        ),
        migrations.AlterField(
            model_name='typedeparentedindividus',
            name='classement',
            field=models.SmallIntegerField(default=1, verbose_name='classement', db_index=True),
        ),
        migrations.AlterField(
            model_name='typedeparentedindividus',
            name='nom',
            field=models.CharField(max_length=100, verbose_name='nom', help_text='En minuscules.', db_index=True),
        ),
        migrations.AlterField(
            model_name='typedeparentedindividus',
            name='nom_pluriel',
            field=models.CharField(max_length=55, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True),
        ),
        migrations.AlterField(
            model_name='typedeparentedindividus',
            name='nom_relatif',
            field=models.CharField(max_length=100, verbose_name='nom relatif', help_text='En minuscules.', db_index=True),
        ),
        migrations.AlterField(
            model_name='typedeparentedoeuvres',
            name='classement',
            field=models.SmallIntegerField(default=1, verbose_name='classement', db_index=True),
        ),
        migrations.AlterField(
            model_name='typedeparentedoeuvres',
            name='nom',
            field=models.CharField(max_length=100, verbose_name='nom', help_text='En minuscules.', db_index=True),
        ),
        migrations.AlterField(
            model_name='typedeparentedoeuvres',
            name='nom_pluriel',
            field=models.CharField(max_length=55, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True),
        ),
        migrations.AlterField(
            model_name='typedeparentedoeuvres',
            name='nom_relatif',
            field=models.CharField(max_length=100, verbose_name='nom relatif', help_text='En minuscules.', db_index=True),
        ),
        migrations.AlterField(
            model_name='typedesource',
            name='nom',
            field=models.CharField(max_length=200, verbose_name='nom', help_text='En minuscules.', unique=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='typedesource',
            name='nom_pluriel',
            field=models.CharField(max_length=230, verbose_name='nom (au pluriel)', help_text='À remplir si le pluriel n’est pas un simple ajout de « s ». Exemple : « animal » devient « animaux » et non « animals ».', blank=True, db_index=True),
        ),
        migrations.AlterField(
            model_name='typedesource',
            name='slug',
            field=autoslug.fields.AutoSlugField(slugify=libretto.models.base.slugify_unicode, always_update=True, editable=False, populate_from='get_slug'),
        ),
    ]
