import os
from django.core.management.base import BaseCommand
from django.db import connections
from django.db.utils import OperationalError


class Command(BaseCommand):
    help = "Check access to database and that env var are set"

    def handle(self, *args, **options):

        unset = []
        for env in [
            "MASTER_MINION_ID",
            "DB_BACKEND",
            "DB_NAME",
            "DB_USER",
            "DB_PASS",
            "DB_HOST",
            "DB_PORT",
            "SECRET_KEY",
            "ALLOWED_HOSTS",
            "SALT_USER",
            "SALT_PASS",
            "SALT_URL",
            "SALT_AUTH",
        ]:
            try:
                os.environ[env]
            except KeyError:
                unset.append(env)

        db_conn = connections["default"]
        try:
            db_conn.cursor()
        except OperationalError as e:
            error = e
        else:
            error = None

        # NOTE: This can simplified with f-string:
        # f"db:\t{error or 'ok'}\nenv:\t{unset or 'ok'}"
        # Or is the use of str.format for compatibility reason ?
        # If so a tox configuration may be necessary.
        self.stdout.write("db:\t{}\nenv:\t{}".format(error or "ok", unset or "ok"))
