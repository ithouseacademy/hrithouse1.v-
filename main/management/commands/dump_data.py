import json
import os
from django.core.management.base import BaseCommand
from django.core import serializers
from main.models import (
    Xodim, BonusRecord, JarimaRecord, BonusSabab, JarimaSabab,
    OzgartirishTarixi, Reyting, Category, Product, ProductOrder,
    PointTransaction, Notification, PushSubscription
)
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'SQLite bazasidan ma\'lumotlarni JSON formatida export qiladi'

    def handle(self, *args, **options):
        data = []

        # 1. Users (superuser va oddiy userlar)
        users = User.objects.all()
        user_data = serializers.serialize('python', users)
        data.extend(user_data)
        self.stdout.write(self.style.SUCCESS(f'Users: {len(users)} ta'))

        # 2. BonusSabab
        items = BonusSabab.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'BonusSabab: {len(items)} ta'))

        # 3. JarimaSabab
        items = JarimaSabab.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'JarimaSabab: {len(items)} ta'))

        # 4. Xodim
        items = Xodim.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'Xodim: {len(items)} ta'))

        # 5. BonusRecord
        items = BonusRecord.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'BonusRecord: {len(items)} ta'))

        # 6. JarimaRecord
        items = JarimaRecord.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'JarimaRecord: {len(items)} ta'))

        # 7. OzgartirishTarixi
        items = OzgartirishTarixi.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'OzgartirishTarixi: {len(items)} ta'))

        # 8. Reyting
        items = Reyting.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'Reyting: {len(items)} ta'))

        # 9. Category
        items = Category.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'Category: {len(items)} ta'))

        # 10. Product
        items = Product.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'Product: {len(items)} ta'))

        # 11. ProductOrder
        items = ProductOrder.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'ProductOrder: {len(items)} ta'))

        # 12. PointTransaction
        items = PointTransaction.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'PointTransaction: {len(items)} ta'))

        # 13. Notification
        items = Notification.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'Notification: {len(items)} ta'))

        # 14. PushSubscription
        items = PushSubscription.objects.all()
        data.extend(serializers.serialize('python', items))
        self.stdout.write(self.style.SUCCESS(f'PushSubscription: {len(items)} ta'))

        # Faylga yozish
        output_file = os.path.join(options.get('output', 'db_dump.json'))
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2, default=str)

        self.stdout.write(self.style.SUCCESS(
            f'\nBarcha ma\'lumotlar {output_file} fayliga saqlandi!'
        ))
        self.stdout.write(self.style.SUCCESS(f'Jami: {len(data)} yozuv'))

    def add_arguments(self, parser):
        parser.add_argument(
            '--output',
            type=str,
            default='db_dump.json',
            help='Chiqish fayli nomi (default: db_dump.json)',
        )
