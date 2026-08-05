from django.db import migrations


def fix_sequences_forward(apps, schema_editor):
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            for table in ('main_jarimarecord', 'main_bonusrecord'):
                cursor.execute(
                    f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
                    f"COALESCE((SELECT MAX(id) FROM {table}), 1));"
                )


def fix_sequences_backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_sitesettings_telegram_thread_id'),
    ]

    operations = [
        migrations.RunPython(fix_sequences_forward, fix_sequences_backward),
    ]
