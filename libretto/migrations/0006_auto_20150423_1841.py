from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0005_auto_20150423_0910'),
    ]

    operations = [
        migrations.AlterField(
            model_name='elementdeprogramme',
            name='oeuvre',
            field=models.ForeignKey(related_name='elements_de_programme', on_delete=django.db.models.deletion.PROTECT, blank=True, to='libretto.Oeuvre', help_text='Vous pouvez croiser le titre et le nom des auteurs. \xc9vitez les termes g\xe9n\xe9raux comme \xab\xa0de\xa0\xbb, \xab\xa0la\xa0\xbb, \xab\xa0le\xa0\xbb, \xab\xa0avec\xa0\xbb.', null=True, verbose_name='work'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_heure_approx',
            field=models.CharField(help_text='Ne remplir que si l\u2019heure est impr\xe9cise.', max_length=30, verbose_name='heure (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='debut_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_heure_approx',
            field=models.CharField(help_text='Ne remplir que si l\u2019heure est impr\xe9cise.', max_length=30, verbose_name='heure (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='evenement',
            name='fin_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='deces_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='deces_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='naissance_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='individu',
            name='naissance_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_heure_approx',
            field=models.CharField(help_text='Ne remplir que si l\u2019heure est impr\xe9cise.', max_length=30, verbose_name='heure (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='creation_lieu_approx',
            field=models.CharField(help_text='Ne remplir que si le lieu (ou institution) est impr\xe9cis(e).', max_length=50, verbose_name='lieu (approximatif)', db_index=True, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='oeuvre',
            name='type_extrait',
            field=models.PositiveSmallIntegerField(blank=True, null=True, verbose_name='type d\u2019extrait', db_index=True, choices=[(1, 'acte'), (2, 'tableau'), (3, 'sc\xe8ne'), (4, 'morceau chant\xe9'), (5, 'partie d\u2019oratorio'), (6, 'livre'), (7, 'album'), (8, 'volume'), (9, 'cahier'), (10, 'ordre'), (11, 'mouvement'), (12, 'pi\xe8ce de recueil')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='source',
            name='date_approx',
            field=models.CharField(help_text='Ne remplir que si la date est impr\xe9cise.', max_length=60, verbose_name='date (approximative)', db_index=True, blank=True),
            preserve_default=True,
        ),
    ]
