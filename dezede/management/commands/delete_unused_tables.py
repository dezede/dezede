from __future__ import print_function
from django.db import connection, transaction
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    help = 'Deletes database tables that are not used by the installed apps.'

    def handle(self, *args, **options):
        cursor = connection.cursor()
        cursor.execute("SELECT * from INFORMATION_SCHEMA.views "
                       "WHERE table_schema = 'public'")
        views = [v[2] for v in cursor.fetchall()]

        tables = connection.introspection.table_names()
        register_tables = connection.introspection.django_table_names()
        tables = sorted(set(tables) - set(register_tables) - set(views))

        for table in tables:
            relations = connection.introspection.get_relations(cursor, table)
            for (_, other_table) in relations.values():
                if other_table in tables:
                    i1 = tables.index(table)
                    i2 = tables.index(other_table)
                    if i1 > i2:
                        tables.pop(i1)
                        tables.insert(i2, table)

        if not tables:
            print('Every database table is registered by Django')
            return

        print('Those tables are not registered by Django:')
        for table in tables:
            print('    ' + table)

        while True:
            delete = raw_input('\nDo you want to delete them? [y|n] ').lower()
            if delete and delete in 'yn':
                break
            print('Invalid choice, you must enter "y" or "n".')

        if delete == 'n':
            return

        with transaction.commit_on_success():
            for table in tables:
                cursor.execute('DROP TABLE %s' % table)
