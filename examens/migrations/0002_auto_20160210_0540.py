from django.db import migrations, models


LEVELS_DATA = (
    (1, (6107, 10442, 10531)),
    (2, (2253, 12468, 12469)),
    (3, (10603, 8167, 10447)),
    (4, (8280, 15117)),
    (5, (3412, 14)),
    (6, (2256,)),
)

LEVELS_HELPS = {
    1: """
    <p>
      L’exercice consiste à transcrire un ensemble de sources
      de manière diplomatique.
      Il comporte six étapes à la difficulté croissante.
      Chaque étape est validée lorsque le texte saisi
      correspond exactement au texte contenu dans la source.
    </p>
    <p>
      Pour ce type de transcription, il est important de respecter
      le texte de la source : graphie fautive, style (capitales,
      petites capitales, etc.), abréviations, ponctuation.
      Deux exceptions sont admises :
    </p>
    <ul>
      <li>
        l’accentuation doit être rétablie suivant l’usage moderne
        (y compris sur les majuscules) ;
      </li>
      <li>
        la justification ne doit pas être respectée :
        vous devez aligner le texte à gauche.
      </li>
    </ul>
    """,
    2: """
    <p>
      Mêmes règles que pour la première étape.
      On insiste cette fois-ci sur le respect des styles
      (capitales, petites capitales, italique, gras, exposant).
    </p>
    """,
    3: """
    <p>
      Dans une transcription diplomatique, l’usage est de respecter
      les graphies fautives. Dans ce cas, le mot erroné doit être suivi
      de la locution latine « sic » en italique et entre crochets carrés.
      Par exemple : « Beethowen [<em>sic</em>] ».
    </p>
    """,
    4: """<p>Combinaison des règles précédentes.</p>""",
    5: """
    <p>
      Combinaison des règles précédentes sur une transcription plus longue.
    </p>
    <p>
      Certaines fautes apparentes pour un lecteur d’aujourd’hui sont en fait
      des usages d’orthographe de l’époque.
      Par exemple, on écrivait indifféremment « accents » ou « accens »
      pour le pluriel d’« accent ».
    </p>
    <p>Conservez l’orthographe des noms propres.</p>
    """,
    6: """
    <p>
      Utilisez les outils de tableau de l’éditeur de texte
      pour obtenir un tableau sans bordure.
      Ne pas inclure les points servant de guides dans le tableau.
    </p>
    """,
}


def add_levels(apps, schema_editor):
    Level = apps.get_model('examens.Level')
    LevelSource = apps.get_model('examens.LevelSource')
    Source = apps.get_model('libretto.Source')

    level_sources = []
    for level_number, source_ids in LEVELS_DATA:
        level = Level.objects.create(
            number=level_number, help_message=LEVELS_HELPS[level_number])
        for pk in source_ids:
            try:
                source = Source.objects.get(pk=pk)
            except Source.DoesNotExist:
                continue
            level_sources.append(LevelSource(level=level, source=source))
    LevelSource.objects.bulk_create(level_sources)


class Migration(migrations.Migration):

    dependencies = [
        ('examens', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_levels),
    ]
