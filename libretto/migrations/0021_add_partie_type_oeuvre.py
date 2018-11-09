from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0020_removes_4_unused_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='partie',
            name='oeuvre2',
            field=models.ForeignKey(related_name='parties', verbose_name='work', blank=True, to='libretto.Oeuvre', help_text='Ne remplir que pour les r\xf4les.', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='partie',
            name='type',
            field=models.PositiveSmallIntegerField(default=0, verbose_name='type', choices=[(1, 'instrument'), (2, 'r\xf4le')]),
            preserve_default=False,
        ),
    ]
