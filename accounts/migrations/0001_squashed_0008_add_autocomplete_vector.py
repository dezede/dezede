# Generated by Django 3.2.13 on 2024-04-09 14:57

import accounts.models
import db_search.sql
from django.conf import settings
import django.contrib.auth.validators
import django.contrib.postgres.indexes
import django.contrib.postgres.search
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.expressions
import django.utils.timezone
import tree.fields
import tree.operations


class Migration(migrations.Migration):

    replaces = [('accounts', '0001_initial'), ('accounts', '0002_auto_20160226_1548'), ('accounts', '0003_mptt_to_tree'), ('accounts', '0004_auto_20210627_2325'), ('accounts', '0005_migrate_tree'), ('accounts', '0006_auto_20230706_2033'), ('accounts', '0007_add_search_vectors'), ('accounts', '0008_add_autocomplete_vector')]

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        ('auth', '0001_initial'),
        ('contenttypes', '0001_initial'),
        ('tree', '0001_initial'),
        ('db_search', '0001_create_search_configurations'),
    ]

    operations = [
        migrations.CreateModel(
            name='HierarchicUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')], verbose_name='username')),
                ('first_name', models.CharField(blank=True, max_length=30, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=75, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=75, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('show_email', models.BooleanField(default=False, verbose_name='afficher l’email')),
                ('website', models.URLField(blank=True, verbose_name='site internet')),
                ('website_verbose', models.CharField(blank=True, max_length=50, verbose_name='nom affiché du site internet')),
                ('legal_person', models.BooleanField(default=False, help_text='Cochez si vous êtes une institution ou un ensemble.', verbose_name='personne morale')),
                ('object_id', models.PositiveIntegerField(blank=True, null=True, verbose_name='identifiant de l’autorité associée')),
                ('willing_to_be_mentor', models.BooleanField(default=False, verbose_name='Veut être mentor')),
                ('avatar', models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='avatar')),
                ('presentation', models.TextField(blank=True, validators=[django.core.validators.MaxLengthValidator(5000)], verbose_name='présentation')),
                ('fonctions', models.TextField(blank=True, validators=[django.core.validators.MaxLengthValidator(200)], verbose_name='fonctions au sein de l’équipe')),
                ('literature', models.TextField(blank=True, verbose_name='publications')),
                ('lft', models.PositiveIntegerField(db_index=True, editable=False)),
                ('rght', models.PositiveIntegerField(db_index=True, editable=False)),
                ('tree_id', models.PositiveIntegerField(db_index=True, editable=False)),
                ('level', models.PositiveIntegerField(db_index=True, editable=False)),
                ('content_type', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='type d’autorité associée')),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups')),
                ('mentor', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disciples', to=settings.AUTH_USER_MODEL, verbose_name='mentor')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.Permission', verbose_name='user permissions')),
            ],
            options={
                'ordering': ('last_name', 'first_name'),
                'verbose_name': 'utilisateur',
                'verbose_name_plural': 'utilisateurs',
            },
        ),
        migrations.AlterModelManagers(
            name='hierarchicuser',
            managers=[
                ('objects', accounts.models.HierarchicUserManager()),
            ],
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='groups',
            field=models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.Group', verbose_name='groups'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=30, unique=True, validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username. This value may contain only letters, numbers and @/./+/-/_ characters.')], verbose_name='username'),
        ),
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='level',
        ),
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='lft',
        ),
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='rght',
        ),
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='tree_id',
        ),
        migrations.AddField(
            model_name='hierarchicuser',
            name='path',
            field=tree.fields.PathField(db_index=True, order_by=['last_name', 'first_name', 'username'], parent_field_name='mentor'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='avatar',
            field=models.ImageField(blank=True, null=True, upload_to='avatars/', verbose_name='photographie d’identité'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='mentor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disciples', to=settings.AUTH_USER_MODEL, verbose_name='responsable scientifique'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='willing_to_be_mentor',
            field=models.BooleanField(default=False, verbose_name='Veut être responsable scientifique'),
        ),
        tree.operations.CreateTreeTrigger(
            model_lookup='hierarchicuser',
        ),
        tree.operations.RebuildPaths(
            model_lookup='hierarchicuser',
        ),
        tree.operations.DeleteTreeTrigger(
            model_lookup='hierarchicuser',
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='content_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'model__in': ('partie', 'profession', 'oeuvre', 'ensemble', 'source', 'lieu', 'evenement', 'individu')}, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='type d’autorité associée'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='first_name',
            field=models.CharField(blank=True, max_length=150, verbose_name='first name'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='mentor',
            field=models.ForeignKey(blank=True, limit_choices_to={'willing_to_be_mentor__exact': True}, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='disciples', to=settings.AUTH_USER_MODEL, verbose_name='responsable scientifique'),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='username',
            field=models.CharField(error_messages={'unique': 'A user with that username already exists.'}, help_text='Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.', max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name='username'),
        ),
        tree.operations.CreateTreeTrigger(
            model_lookup='hierarchicuser',
        ),
        tree.operations.RebuildPaths(
            model_lookup='hierarchicuser',
        ),
        tree.operations.DeleteTreeTrigger(
            model_lookup='hierarchicuser',
        ),
        migrations.RemoveField(
            model_name='hierarchicuser',
            name='path',
        ),
        migrations.AddField(
            model_name='hierarchicuser',
            name='path',
            field=tree.fields.PathField(db_index=True, order_by=['last_name', 'first_name', 'username'], parent_field_name='mentor'),
        ),
        tree.operations.CreateTreeTrigger(
            model_lookup='hierarchicuser',
        ),
        tree.operations.RebuildPaths(
            model_lookup='hierarchicuser',
        ),
        migrations.AlterModelOptions(
            name='hierarchicuser',
            options={'ordering': ['last_name', 'first_name'], 'verbose_name': 'utilisateur', 'verbose_name_plural': 'utilisateurs'},
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='content_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'model__in': ('individu', 'profession', 'source', 'evenement', 'ensemble', 'partie', 'lieu', 'oeuvre')}, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='type d’autorité associée'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=models.Index(django.db.models.expressions.RawSQL('path[:array_length(path, 1) - 1]', ()), name='user_path_parent_index'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=models.Index(django.db.models.expressions.F('path__level'), name='user_path_level_index'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=models.Index(django.db.models.expressions.F('path__0_1'), name='user_path_slice_1_index'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=models.Index(django.db.models.expressions.F('path__0_2'), name='user_path_slice_2_index'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=models.Index(django.db.models.expressions.F('path__0_3'), name='user_path_slice_3_index'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=models.Index(django.db.models.expressions.F('path__0_4'), name='user_path_slice_4_index'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=models.Index(django.db.models.expressions.F('path__0_5'), name='user_path_slice_5_index'),
        ),
        migrations.AddField(
            model_name='hierarchicuser',
            name='search_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='content_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'model__in': ('source', 'evenement', 'lieu', 'individu', 'profession', 'ensemble', 'oeuvre', 'partie')}, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='type d’autorité associée'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('search_vector'), name='hierarchicuser_search'),
        ),
        migrations.AddField(
            model_name='hierarchicuser',
            name='autocomplete_vector',
            field=django.contrib.postgres.search.SearchVectorField(blank=True, editable=False, null=True),
        ),
        migrations.AlterField(
            model_name='hierarchicuser',
            name='content_type',
            field=models.ForeignKey(blank=True, limit_choices_to={'model__in': ('lieu', 'oeuvre', 'evenement', 'ensemble', 'profession', 'partie', 'source', 'individu')}, null=True, on_delete=django.db.models.deletion.CASCADE, to='contenttypes.contenttype', verbose_name='type d’autorité associée'),
        ),
        migrations.AddIndex(
            model_name='hierarchicuser',
            index=django.contrib.postgres.indexes.GinIndex(django.db.models.expressions.F('autocomplete_vector'), name='hierarchicuser_autocomplete'),
        ),
    ]