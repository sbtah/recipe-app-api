"""
Django command to wait for database to be available.
"""
import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """
    Django command to wait for database.
    """

    def handle(self, *args, **kwargs):
        """Entrypoint for command."""

        self.stdout.write(self.style.NOTICE("Waiting for database..."))
        db_up = False
        while db_up is False:
            try:
                self.check(databases=["default"])
                db_up = True
            except (Psycopg2Error, OperationalError):
                self.stderr.write(
                    self.style.ERROR(
                        "Database unavailable, waiting 1 second...",
                    )
                )
                time.sleep(1)

        self.stdout.write(self.style.SUCCESS("Database available!"))
