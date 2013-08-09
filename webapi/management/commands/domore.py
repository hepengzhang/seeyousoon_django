from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
import MySQLdb as database
from warnings import filterwarnings

filterwarnings('ignore', category=database.Warning)

class Command(BaseCommand):
    args = ''
    help = 'Drop database and create database'

    def handle(self, *args, **options):
        try:
            c = connection.cursor()
            fulltextindex = "CREATE FULLTEXT INDEX `webapi_user_search_index` ON `webapi_user_search` (username, name);"
            c.execute(fulltextindex)
            transaction.commit_unless_managed()
            self.stdout.write("FULLTEXT INDEX on user_search created")
        except Warning as e:
            raise CommandError(str(type(e))+str(e))