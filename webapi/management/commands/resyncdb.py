from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from SYSBackend import settings

class Command(BaseCommand):
    args = ''
    help = 'Drop database and create database'

    def handle(self, *args, **options):
        dbname = settings.DATABASES['default']['NAME']
        try:
            c = connection.cursor()
            drop = "DROP DATABASE IF EXISTS " + dbname + ""
            c.execute(drop)
            create = "CREATE DATABASE " + dbname
            c.execute(create)
            transaction.commit_unless_managed()
            self.stdout.write("database dropped and created")
        except Exception as e:
            raise CommandError(str(e))