from django.conf import settings
from django.db import migrations, models
from django.utils.html import escapejs
from django.utils.translation import activate
import django.db.models.deletion
import modelcluster.fields
import wagtail.fields

from common.utils.text import str_list


def move_sender(apps, schema_editor):
    Letter = apps.get_model('correspondence.Letter')
    LetterSender = apps.get_model('correspondence.LetterSender')
    bulk = []
    for letter in Letter.objects.only('pk', 'sender_id'):
        bulk.append(LetterSender(letter=letter, person_id=letter.sender_id))
    LetterSender.objects.bulk_create(bulk)


def move_references(apps, schema_editor):
    activate(settings.LANGUAGE_CODE)
    Letter = apps.get_model('correspondence.Letter')
    for letter in Letter.objects.prefetch_related('letter_images'):
        reference_links = []
        for image in letter.letter_images.all():
            for reference in image.references:
                instance = reference.value
                reference_links.append(
                    f'<a linktype="{instance._meta.model_name}-link" '
                    f'id="{instance.pk}" data-string="{escapejs(str(instance))}" '
                    f'data-app-name="{instance._meta.app_label}" '
                    f'data-model-name="{instance._meta.model_name}">{instance}</a>'
                )
        if reference_links:
            letter.transcription += f'<p>Références : {str_list(reference_links)}</p>'
        letter.save()


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0003_alter_auteur_owner_and_more'),
        ('correspondence', '0004_auto_20250906_0008'),
    ]

    operations = [
        migrations.AlterField(
            model_name='letter',
            name='writing_date',
            field=models.DateField(blank=True, db_index=True, help_text='Exemple\xa0: « 1789-7-14 » pour le 14 juillet 1789. En cas de date approximative, saisir le premier jour du mois («\xa01678-10-1\xa0» pour octobre 1678) ou de l’année («\xa01830-1-1\xa0» pour 1830).', null=True, verbose_name='date'),
        ),
        migrations.AlterField(
            model_name='lettercorpus',
            name='body',
            field=wagtail.fields.StreamField([('text', 0), ('pages_row', 2), ('images_row', 9)], blank=True, block_lookup={0: ('wagtail.blocks.RichTextBlock', (), {'label': 'Texte'}), 1: ('correspondence.blocks.CustomPageBlock', (), {'search_index': False}), 2: ('wagtail.blocks.ListBlock', (1,), {'icon': 'doc-empty-inverse', 'label': 'Rangée de pages', 'search_index': False}), 3: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('small', 'petite'), ('default', 'par défaut'), ('large', 'grande')], 'label': 'Hauteur'}), 4: ('correspondence.blocks.CustomImageBlock', (), {'label': 'Image', 'search_index': False}), 5: ('wagtail.blocks.URLBlock', (), {'label': 'URL du lien', 'required': False, 'search_index': False}), 6: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('narrow', 'étroite'), ('default', 'par défaut'), ('wide', 'large')], 'label': 'Largeur'}), 7: ('wagtail.blocks.StructBlock', [[('image', 4), ('link_url', 5), ('width', 6)]], {'label': 'Image'}), 8: ('wagtail.blocks.ListBlock', (7,), {'label': 'Images', 'search_index': False}), 9: ('wagtail.blocks.StructBlock', [[('height', 3), ('images', 8)]], {'label': 'Rangée d’images'})}, verbose_name='contenu'),
        ),
        migrations.AlterField(
            model_name='letterindex',
            name='body',
            field=wagtail.fields.StreamField([('text', 0), ('pages_row', 2), ('images_row', 9)], blank=True, block_lookup={0: ('wagtail.blocks.RichTextBlock', (), {'label': 'Texte'}), 1: ('correspondence.blocks.CustomPageBlock', (), {'search_index': False}), 2: ('wagtail.blocks.ListBlock', (1,), {'icon': 'doc-empty-inverse', 'label': 'Rangée de pages', 'search_index': False}), 3: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('small', 'petite'), ('default', 'par défaut'), ('large', 'grande')], 'label': 'Hauteur'}), 4: ('correspondence.blocks.CustomImageBlock', (), {'label': 'Image', 'search_index': False}), 5: ('wagtail.blocks.URLBlock', (), {'label': 'URL du lien', 'required': False, 'search_index': False}), 6: ('wagtail.blocks.ChoiceBlock', [], {'choices': [('narrow', 'étroite'), ('default', 'par défaut'), ('wide', 'large')], 'label': 'Largeur'}), 7: ('wagtail.blocks.StructBlock', [[('image', 4), ('link_url', 5), ('width', 6)]], {'label': 'Image'}), 8: ('wagtail.blocks.ListBlock', (7,), {'label': 'Images', 'search_index': False}), 9: ('wagtail.blocks.StructBlock', [[('height', 3), ('images', 8)]], {'label': 'Rangée d’images'})}, verbose_name='contenu'),
        ),
        migrations.CreateModel(
            name='LetterSender',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sort_order', models.IntegerField(blank=True, editable=False, null=True)),
                ('letter', modelcluster.fields.ParentalKey(on_delete=django.db.models.deletion.CASCADE, related_name='senders', to='correspondence.letter')),
                ('person', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='letter_senders', to='libretto.individu', verbose_name='individu')),
            ],
            options={
                'verbose_name': 'expéditeur',
                'verbose_name_plural': 'expéditeurs',
                'ordering': ['sort_order'],
                'abstract': False,
            },
        ),
        migrations.RunPython(move_sender),
        migrations.RemoveField(
            model_name='letter',
            name='sender',
        ),
        migrations.AddField(
            model_name='letter',
            name='sender_persons',
            field=models.ManyToManyField(related_name='sent_letters', through='correspondence.LetterSender', to='libretto.individu'),
        ),
        migrations.RunPython(move_references),
        migrations.RemoveField(
            model_name='letterimage',
            name='references',
        ),
    ]
