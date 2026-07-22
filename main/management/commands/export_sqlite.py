import sqlite3
import os
import tempfile
from decimal import Decimal
from datetime import datetime, date

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db import connection
from django.conf import settings


class Command(BaseCommand):
    help = 'PostgreSQL bazasidan db.sqlite3 fayl yaratadi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='db.sqlite3',
            help='Chiqish fayli nomi (default: db.sqlite3)',
        )

    def handle(self, *args, **options):
        output_path = options['output']

        with connection.cursor() as pg_cursor:
            pg_cursor.execute(
                "SELECT table_name FROM information_schema.tables "
                "WHERE table_schema = 'public' ORDER BY table_name"
            )
            tables = [row[0] for row in pg_cursor.fetchall()]

            self.stdout.write(self.style.SUCCESS(f'PostgreSQL da {len(tables)} ta jadval topildi'))

            if os.path.exists(output_path):
                os.remove(output_path)

            sqlite_conn = sqlite3.connect(output_path)
            sqlite_cursor = sqlite_conn.cursor()

            for table_name in tables:
                pg_cursor.execute(f'SELECT column_name, data_type, character_maximum_length '
                                  f'FROM information_schema.columns '
                                  f'WHERE table_name = %s ORDER BY ordinal_position', [table_name])
                columns_info = pg_cursor.fetchall()

                if not columns_info:
                    continue

                col_defs = []
                for col_name, data_type, max_len in columns_info:
                    pg_type = data_type.lower()
                    if pg_type in ('bigint', 'integer', 'smallint', 'serial', 'bigserial'):
                        col_type = 'INTEGER'
                    elif pg_type in ('boolean',):
                        col_type = 'INTEGER'
                    elif pg_type in ('decimal', 'numeric', 'real', 'double precision'):
                        col_type = 'REAL'
                    elif pg_type in ('date',):
                        col_type = 'TEXT'
                    elif pg_type in ('timestamp without time zone', 'timestamp with time zone', 'datetime'):
                        col_type = 'TEXT'
                    elif pg_type in ('bytea',):
                        col_type = 'BLOB'
                    else:
                        col_type = 'TEXT'
                    col_defs.append(f'"{col_name}" {col_type}')

                create_sql = f'CREATE TABLE IF NOT EXISTS "{table_name}" ({", ".join(col_defs)})'
                sqlite_cursor.execute(create_sql)

                pg_cursor.execute(f'SELECT * FROM "{table_name}"')
                rows = pg_cursor.fetchall()

                if rows:
                    col_names = [col[0] for col in columns_info]
                    placeholders = ', '.join(['?' for _ in col_names])
                    insert_sql = f'INSERT INTO "{table_name}" ({", ".join([f"{c}" for c in col_names])}) VALUES ({placeholders})'

                    cleaned_rows = []
                    for row in rows:
                        cleaned = []
                        for val in row:
                            if val is None:
                                cleaned.append(None)
                            elif isinstance(val, datetime):
                                cleaned.append(val.isoformat())
                            elif isinstance(val, date):
                                cleaned.append(val.isoformat())
                            elif isinstance(val, Decimal):
                                cleaned.append(float(val))
                            elif isinstance(val, bool):
                                cleaned.append(1 if val else 0)
                            elif isinstance(val, bytes):
                                cleaned.append(val)
                            else:
                                cleaned.append(str(val) if not isinstance(val, (int, float)) else val)
                        cleaned_rows.append(cleaned)

                    sqlite_cursor.executemany(insert_sql, cleaned_rows)

                self.stdout.write(self.style.SUCCESS(f'  {table_name}: {len(rows)} ta yozuv'))

            sqlite_conn.commit()
            sqlite_conn.close()

        file_size = os.path.getsize(output_path)
        size_mb = file_size / (1024 * 1024)
        self.stdout.write(self.style.SUCCESS(
            f'\nSQLite fayl yaratildi: {output_path} ({size_mb:.2f} MB)'
        ))
