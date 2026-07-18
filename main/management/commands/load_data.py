import json
import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import (
    Xodim, BonusRecord, JarimaRecord, BonusSabab, JarimaSabab,
    OzgartirishTarixi, Reyting, Category, Product, ProductOrder,
    PointTransaction, Notification, PushSubscription
)


class Command(BaseCommand):
    help = 'JSON fayldan ma\'lumotlarni PostgreSQL bazasiga import qiladi'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='db_dump.json',
            help='Import fayli nomi (default: db_dump.json)',
        )

    def handle(self, *args, **options):
        input_file = options.get('file', 'db_dump.json')

        if not os.path.exists(input_file):
            self.stdout.write(self.style.ERROR(f'{input_file} fayli topilmadi!'))
            return

        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write(self.style.SUCCESS(f'Jami {len(data)} yozuv topildi'))

        # Model tartibi (ForeignKey bog'liqligiga qarab)
        model_order = [
            'User',
            'BonusSabab',
            'JarimaSabab',
            'Xodim',
            'BonusRecord',
            'JarimaRecord',
            'OzgartirishTarixi',
            'Reyting',
            'Category',
            'Product',
            'ProductOrder',
            'PointTransaction',
            'Notification',
            'PushSubscription',
        ]

        model_map = {
            'auth.User': User,
            'main.BonusSabab': BonusSabab,
            'main.JarimaSabab': JarimaSabab,
            'main.Xodim': Xodim,
            'main.BonusRecord': BonusRecord,
            'main.JarimaRecord': JarimaRecord,
            'main.OzgartirishTarixi': OzgartirishTarixi,
            'main.Reyting': Reyting,
            'main.Category': Category,
            'main.Product': Product,
            'main.ProductOrder': ProductOrder,
            'main.PointTransaction': PointTransaction,
            'main.Notification': Notification,
            'main.PushSubscription': PushSubscription,
        }

        # Ma'lumotlarni model bo'yicha guruhlash
        grouped = {}
        for item in data:
            model_name = item['model']
            if model_name not in grouped:
                grouped[model_name] = []
            grouped[model_name].append(item)

        # Har bir model uchun import
        for model_name in model_order:
            # auth.User uchun 'auth.User' yoki 'User' bo'lishi mumkin
            possible_keys = [model_name, f'auth.{model_name}', f'main.{model_name}']
            items = []
            for key in possible_keys:
                if key in grouped:
                    items = grouped.pop(key)
                    break

            if not items:
                continue

            model = model_map.get(model_name) or model_map.get(f'main.{model_name}')
            if not model:
                self.stdout.write(self.style.WARNING(f'{model_name} modeli topilmadi, o\'tkazib yuborildi'))
                continue

            count = 0
            for item in items:
                fields = item['fields']
                pk = item.get('pk')

                # ForeignKey maydonlarini ID ga aylantirish
                foreign_keys = {}
                for field_name, value in fields.items():
                    if isinstance(value, dict) and 'pk' in value:
                        foreign_keys[field_name] = value['pk']
                    elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict) and 'pk' in value[0]:
                        foreign_keys[field_name] = value[0]['pk']

                # ForeignKey qiymatlarini qo'yish
                for field_name, pk_value in foreign_keys.items():
                    fields[field_name] = pk_value

                try:
                    obj, created = model.objects.update_or_create(
                        pk=pk,
                        defaults=fields
                    )
                    if created:
                        count += 1
                except Exception as e:
                    self.stdout.write(self.style.WARNING(
                        f'Xato ({model_name} pk={pk}): {e}'
                    ))

            total = model.objects.count()
            self.stdout.write(self.style.SUCCESS(
                f'{model_name}: {count} ta yangi, jami {total} ta'
            ))

        # Qolgan guruhlarni import qilish (agar model_order da yo'q bo'lsa)
        for model_name, items in grouped.items():
            self.stdout.write(self.style.WARNING(
                f'{model_name} modeli model_order da yo\'q, o\'tkazib yuborildi'
            ))

        self.stdout.write(self.style.SUCCESS('\nImport tugadi!'))
