# Generated by Django 3.2.13 on 2024-02-05 17:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('libretto', '0062_fix_numbercharfield_max_length'),
    ]

    operations = [
        migrations.RunSQL("""
                ALTER TABLE libretto_elementdedistribution
                DROP CONSTRAINT individu_xor_ensemble;
            
                ALTER TABLE libretto_elementdedistribution
                DROP CONSTRAINT evenement_xor_elementdeprogramme;

                ALTER TABLE libretto_elementdedistribution
                DROP CONSTRAINT not_partie_and_profession;

                ALTER TABLE libretto_auteur
                DROP CONSTRAINT oeuvre_xor_source;

                ALTER TABLE libretto_auteur
                DROP CONSTRAINT individu_xor_ensemble;
            """,
  """
                ALTER TABLE libretto_elementdedistribution
                ADD CONSTRAINT evenement_xor_elementdeprogramme
                CHECK (evenement_id IS NOT NULL <> element_de_programme_id IS NOT NULL);

                ALTER TABLE libretto_elementdedistribution
                ADD CONSTRAINT not_partie_and_profession
                CHECK (NOT (partie_id IS NOT NULL AND profession_id IS NOT NULL));

                ALTER TABLE libretto_auteur
                ADD CONSTRAINT oeuvre_xor_source
                CHECK (oeuvre_id IS NOT NULL <> source_id IS NOT NULL);

                ALTER TABLE libretto_auteur
                ADD CONSTRAINT individu_xor_ensemble
                CHECK (individu_id IS NOT NULL <> ensemble_id IS NOT NULL);
                
                ALTER TABLE libretto_elementdedistribution
                ADD CONSTRAINT individu_xor_ensemble
                CHECK (individu_id IS NOT NULL <> ensemble_id IS NOT NULL);
            """),
        migrations.AddConstraint(
            model_name='auteur',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('oeuvre__isnull', True), ('source__isnull', False)), models.Q(('oeuvre__isnull', False), ('source__isnull', True)), _connector='OR'), name='auteur_has_oeuvre_xor_source'),
        ),
        migrations.AddConstraint(
            model_name='auteur',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('individu__isnull', True), ('ensemble__isnull', False)), models.Q(('individu__isnull', False), ('ensemble__isnull', True)), _connector='OR'), name='auteur_has_individu_xor_ensemble'),
        ),
        migrations.AddConstraint(
            model_name='elementdedistribution',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('evenement__isnull', True), ('element_de_programme__isnull', False)), models.Q(('evenement__isnull', False), ('element_de_programme__isnull', True)), _connector='OR'), name='distribution_has_evenement_xor_programme'),
        ),
        migrations.AddConstraint(
            model_name='elementdedistribution',
            constraint=models.CheckConstraint(check=models.Q(models.Q(('individu__isnull', True), ('ensemble__isnull', False)), models.Q(('individu__isnull', False), ('ensemble__isnull', True)), _connector='OR'), name='distribution_has_individu_xor_ensemble'),
        ),
        migrations.AddConstraint(
            model_name='elementdedistribution',
            constraint=models.CheckConstraint(check=models.Q(('partie__isnull', False), ('profession__isnull', False), _negated=True), name='distribution_has_not_partie_and_profession'),
        ),
    ]