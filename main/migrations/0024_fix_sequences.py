from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_sitesettings_telegram_thread_id'),
    ]

    operations = [
        migrations.RunSQL(
            sql="SELECT setval(pg_get_serial_sequence('main_jarimarecord', 'id'), COALESCE((SELECT MAX(id) FROM main_jarimarecord), 1));",
            reverse_sql="SELECT 1;",
        ),
        migrations.RunSQL(
            sql="SELECT setval(pg_get_serial_sequence('main_bonusrecord', 'id'), COALESCE((SELECT MAX(id) FROM main_bonusrecord), 1));",
            reverse_sql="SELECT 1;",
        ),
    ]
