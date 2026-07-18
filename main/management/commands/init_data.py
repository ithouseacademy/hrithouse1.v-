import json
import os
from django.core.management.base import BaseCommand
from django.core.management import call_command
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'Database bo\'sh bo\'lsa, fixture dan ma\'lumotlarni yuklaydi'

    def handle(self, *args, **options):
        if User.objects.exists():
            self.stdout.write(self.style.WARNING('Database da ma\'lumotlar mavjud, loaddata o\'tkazib yuborildi'))
            return

        fixture_path = os.path.join('main', 'fixtures', 'dumpdata.json')
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f'{fixture_path} topilmadi'))
            return

        self.stdout.write(self.style.NOTICE('Database bo\'sh, ma\'lumotlar yuklanmoqda...'))

        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        fixture_count = len(data)

        call_command('loaddata', 'main/fixtures/dumpdata.json', verbosity=1)

        user_count = User.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f'Tugadi! {user_count} ta user, jami {fixture_count} yozuv import qilindi'
        ))
