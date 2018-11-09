from django.db import models, migrations
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('libretto', '0015_removes_3_mptt_usages'),
    ]

    operations = [
        migrations.CreateModel(
            name='TypeDeParenteDIndividus2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(help_text='In lowercase.', max_length=100, verbose_name='name', db_index=True)),
                ('nom_pluriel', models.CharField(help_text='\xc0 remplir si le pluriel n\u2019est pas un simple ajout de \xab s \xbb. Exemple : \xab animal \xbb devient \xab animaux \xbb et non \xab animals \xbb.', max_length=55, verbose_name='name (plural)', blank=True)),
                ('nom_relatif', models.CharField(help_text='In lowercase.', max_length=100, verbose_name='nom relatif', db_index=True)),
                ('nom_relatif_pluriel', models.CharField(help_text='\xc0 remplir si le pluriel n\u2019est pas un simple ajout de \xab s \xbb. Exemple : \xab animal \xbb devient \xab animaux \xbb et non \xab animals \xbb.', max_length=130, verbose_name='nom relatif (au pluriel)', blank=True)),
                ('classement', models.SmallIntegerField(default=1, verbose_name='ranking', db_index=True)),
                ('owner', models.ForeignKey(related_name='typedeparentedindividus2', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('classement',),
                'verbose_name': 'type de parent\xe9 d\u2019individus',
                'verbose_name_plural': 'types de parent\xe9 d\u2019individus',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TypeDeParenteDOeuvres2',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nom', models.CharField(help_text='In lowercase.', max_length=100, verbose_name='name', db_index=True)),
                ('nom_pluriel', models.CharField(help_text='\xc0 remplir si le pluriel n\u2019est pas un simple ajout de \xab s \xbb. Exemple : \xab animal \xbb devient \xab animaux \xbb et non \xab animals \xbb.', max_length=55, verbose_name='name (plural)', blank=True)),
                ('nom_relatif', models.CharField(help_text='In lowercase.', max_length=100, verbose_name='nom relatif', db_index=True)),
                ('nom_relatif_pluriel', models.CharField(help_text='\xc0 remplir si le pluriel n\u2019est pas un simple ajout de \xab s \xbb. Exemple : \xab animal \xbb devient \xab animaux \xbb et non \xab animals \xbb.', max_length=130, verbose_name='nom relatif (au pluriel)', blank=True)),
                ('classement', models.SmallIntegerField(default=1, verbose_name='ranking', db_index=True)),
                ('owner', models.ForeignKey(related_name='typedeparentedoeuvres2', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('classement',),
                'verbose_name': 'type de parent\xe9 d\u2019\u0153uvres',
                'verbose_name_plural': 'types de parent\xe9s d\u2019\u0153uvres',
            },
            bases=(models.Model,),
        ),
    ]
