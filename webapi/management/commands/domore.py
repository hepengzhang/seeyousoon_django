from django.core.management.base import BaseCommand, CommandError
from django.db import connection
import sys

class Command(BaseCommand):
    args = ''
    help = 'Create FULLTEXT INDEX on user_search'

    def handle(self, *args, **options):
        try:
            app_name = self.__module__.split('.')[0]
            user_search_table = "{0}_{1}".format(app_name, 'user_search')
            column_name = 'search_index'
            index_name = "{}_{}_fulltext".format(user_search_table, column_name)
            fulltext_create_query = "CREATE FULLTEXT INDEX `{}` ON `{}` ({});".format(index_name, user_search_table,
                                                                                      column_name)
            c = connection.cursor()
            try:
                c.execute(fulltext_create_query)
                print fulltext_create_query
            except Warning as w:
                print "Warning: " + str(w)
            except Exception as e:
                print "Unexpected error:", str(e)
            except:
                print "Unexpected error:", sys.exc_info()[0]
        except Warning as e:
            raise CommandError(str(type(e)) + str(e))