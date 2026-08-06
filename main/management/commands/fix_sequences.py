from django.apps import apps
from django.core.management.base import BaseCommand
from django.db import connection
from django.db.models import AutoField, BigAutoField, SmallAutoField


class Command(BaseCommand):
    help = (
        "PostgreSQL'da barcha jadvallarning id sequence larini MAX(id) ga moslab tiklaydi. "
        "Bu 'duplicate key value violates unique constraint ..._pkey' xatosini oldini oladi "
        "(init_data importi yoki bazani nusxalashdan keyin sequence orqada qoladi)."
    )

    def handle(self, *args, **options):
        if connection.vendor != 'postgresql':
            self.stdout.write(self.style.WARNING("PostgreSQL ishlatilmayapti, hech narsa qilinmadi."))
            return

        fixed = []
        with connection.cursor() as cursor:
            for model in apps.get_models():
                pk = model._meta.pk
                if pk is None or not isinstance(pk, (AutoField, BigAutoField, SmallAutoField)):
                    continue
                table = model._meta.db_table
                try:
                    cursor.execute(
                        f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                        f"COALESCE((SELECT MAX(id) FROM {table}), 1))"
                    )
                    fixed.append(table)
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"{table}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Tayyor: {len(fixed)} ta jadval tuzatildi."))
        for t in sorted(fixed):
            self.stdout.write(f"  - {t}")
