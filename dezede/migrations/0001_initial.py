from django.db import models, migrations
from decimal import Decimal
import dezede.models
import django.db.models.deletion
from django.conf import settings
import image_cropping.fields
import libretto.models.base


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contenttypes', '0001_initial'),
        ('libretto', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Diapositive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(verbose_name='identifiant de l\u2019objet li\xe9')),
                ('title', models.CharField(max_length=70, verbose_name='titre')),
                ('subtitle', models.CharField(max_length=100, verbose_name='sous-titre', blank=True)),
                ('text_align', models.CharField(default='text-left', max_length=11, verbose_name='alignement du texte', choices=[('text-left', 'Gauche'), ('text-center', 'Centre'), ('text-right', 'Droite')])),
                ('text_background', models.BooleanField(default=False, help_text='Ajoute un cadre semi-transparent derri\xe8re le texte pour faciliter la lecture.', verbose_name='cadre derri\xe8re le texte')),
                ('image', models.ImageField(upload_to='accueil', verbose_name='image')),
                ('cropping', image_cropping.fields.ImageRatioField('image', '450x450', hide_image_field=False, size_warning=True, allow_fullsize=False, free_crop=True, adapt_rotation=False, help_text=None, verbose_name='d\xe9coupage de l\u2019image')),
                ('image_align', models.CharField(default='text-right', max_length=11, verbose_name='alignement de l\u2019image', choices=[('text-left', 'Gauche'), ('text-center', 'Centre'), ('text-right', 'Droite')])),
                ('opacity', models.DecimalField(default=0.6, verbose_name='opacit\xe9', max_digits=2, decimal_places=1, choices=[(Decimal('1.0'), 'Opaque'), (Decimal('0.9'), '90 %'), (Decimal('0.8'), '80 %'), (Decimal('0.7'), '70 %'), (Decimal('0.6'), '60 %'), (Decimal('0.5'), '50 %'), (Decimal('0.4'), '40 %'), (Decimal('0.3'), '30 %'), (Decimal('0.2'), '20 %'), (Decimal('0.1'), '10 %')])),
                ('position', models.PositiveSmallIntegerField(default=1, verbose_name='position')),
                ('content_type', models.ForeignKey(verbose_name='type d\u2019objet li\xe9', to='contenttypes.ContentType')),
                ('etat', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, default=libretto.models.base._get_default_etat, verbose_name='\xe9tat', to='libretto.Etat')),
                ('owner', models.ForeignKey(related_name='diapositive', on_delete=django.db.models.deletion.PROTECT, verbose_name='propri\xe9taire', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
            ],
            options={
                'ordering': ('position',),
                'verbose_name': 'diapositive',
                'verbose_name_plural': 'diapositives',
            },
            bases=(models.Model,),
        ),
    ]
