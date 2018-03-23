# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django.core.validators
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HierarchicUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('username', models.CharField(help_text='Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.', unique=True, max_length=30, verbose_name='username', validators=[django.core.validators.RegexValidator('^[\\w.@+-]+$', 'Enter a valid username.', 'invalid')])),
                ('first_name', models.CharField(max_length=30, verbose_name='first name', blank=True)),
                ('last_name', models.CharField(max_length=75, verbose_name='last name', blank=True)),
                ('email', models.EmailField(max_length=75, verbose_name='email address', blank=True)),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('show_email', models.BooleanField(default=False, verbose_name='afficher l\u2019email')),
                ('website', models.URLField(verbose_name='site internet', blank=True)),
                ('website_verbose', models.CharField(max_length=50, verbose_name='nom affich\xe9 du site internet', blank=True)),
                ('legal_person', models.BooleanField(default=False, help_text='Cochez si vous \xeates une institution ou un ensemble.', verbose_name='personne morale')),
                ('object_id', models.PositiveIntegerField(null=True, verbose_name='identifiant de l\u2019autorit\xe9 associ\xe9e', blank=True)),
                ('willing_to_be_mentor', models.BooleanField(default=False, verbose_name='Veut \xeatre mentor')),
                ('avatar', models.ImageField(upload_to='avatars/', null=True, verbose_name='avatar', blank=True)),
                ('presentation', models.TextField(blank=True, verbose_name='pr\xe9sentation', validators=[django.core.validators.MaxLengthValidator(5000)])),
                ('fonctions', models.TextField(blank=True, verbose_name='fonctions au sein de l\u2019\xe9quipe', validators=[django.core.validators.MaxLengthValidator(200)])),
                ('literature', models.TextField(verbose_name='publications', blank=True)),
                ('lft', models.PositiveIntegerField(editable=False, db_index=True)),
                ('rght', models.PositiveIntegerField(editable=False, db_index=True)),
                ('tree_id', models.PositiveIntegerField(editable=False, db_index=True)),
                ('level', models.PositiveIntegerField(editable=False, db_index=True)),
                ('content_type', models.ForeignKey(verbose_name='type d\u2019autorit\xe9 associ\xe9e', blank=True, to='contenttypes.ContentType', null=True)),
                ('groups', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Group', blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.', verbose_name='groups')),
                ('mentor', models.ForeignKey(related_name='disciples', verbose_name='mentor', blank=True, to=settings.AUTH_USER_MODEL, null=True)),
                ('user_permissions', models.ManyToManyField(related_query_name='user', related_name='user_set', to='auth.Permission', blank=True, help_text='Specific permissions for this user.', verbose_name='user permissions')),
            ],
            options={
                'ordering': ('last_name', 'first_name'),
                'verbose_name': 'utilisateur',
                'verbose_name_plural': 'utilisateurs',
            },
            bases=(models.Model,),
        ),
    ]
