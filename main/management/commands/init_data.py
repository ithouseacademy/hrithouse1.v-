import json
import os
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from main.models import (
    BonusSabab, JarimaSabab, Xodim, BonusRecord, JarimaRecord,
    OzgartirishTarixi, Reyting, Category, Product, ProductOrder,
    PointTransaction, Notification, PushSubscription
)


class Command(BaseCommand):
    help = 'SQLite dump JSON dan PostgreSQL ga to\'g\'ridan-to\'g\'ri import'

    def handle(self, *args, **options):
        fixture_path = os.path.join('main', 'fixtures', 'dumpdata.json')
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f'{fixture_path} topilmadi'))
            return

        with open(fixture_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        self.stdout.write(self.style.NOTICE(f'Jami {len(data)} yozuv topildi, import boshlanmoqda...'))

        model_order = [
            'auth.user',
            'auth.group',
            'main.bonussabab',
            'main.jarimasabab',
            'main.xodim',
            'main.bonusrecord',
            'main.jarimarecord',
            'main.ozgartirishtarixi',
            'main.reyting',
            'main.category',
            'main.product',
            'main.productorder',
            'main.pointtransaction',
            'main.notification',
            'main.pushsubscription',
        ]

        model_map = {
            'auth.user': User,
            'main.bonussabab': BonusSabab,
            'main.jarimasabab': JarimaSabab,
            'main.xodim': Xodim,
            'main.bonusrecord': BonusRecord,
            'main.jarimarecord': JarimaRecord,
            'main.ozgartirishtarixi': OzgartirishTarixi,
            'main.reyting': Reyting,
            'main.category': Category,
            'main.product': Product,
            'main.productorder': ProductOrder,
            'main.pointtransaction': PointTransaction,
            'main.notification': Notification,
            'main.pushsubscription': PushSubscription,
        }

        fk_fields = {
            'main.xodim': ['user'],
            'main.bonusrecord': ['xodim', 'sabab', 'created_by'],
            'main.jarimarecord': ['xodim', 'sabab', 'created_by'],
            'main.ozgartirishtarixi': ['xodim', 'admin'],
            'main.reyting': ['xodim'],
            'main.product': ['category'],
            'main.productorder': ['user', 'product'],
            'main.pointtransaction': ['user', 'order'],
            'main.notification': ['user'],
            'main.pushsubscription': ['user'],
        }

        datetime_fields = {
            'main.xodim': ['created_at', 'updated_at'],
            'main.bonusrecord': ['sana'],
            'main.jarimarecord': ['sana'],
            'main.ozgartirishtarixi': ['sana'],
            'main.reyting': ['sana'],
            'main.product': ['created_at'],
            'main.productorder': ['created_at', 'approved_at', 'rejected_at'],
            'main.pointtransaction': ['created_at'],
            'main.notification': ['created_at'],
            'main.pushsubscription': ['created_at'],
            'auth.user': ['last_login', 'date_joined'],
        }

        m2m_fields = {
            'auth.user': ['groups', 'user_permissions'],
        }

        created_count = 0
        updated_count = 0
        error_count = 0

        for model_name in model_order:
            items = [d for d in data if d['model'] == model_name]
            if not items:
                continue

            model = model_map.get(model_name)
            if not model:
                continue

            fk_list = fk_fields.get(model_name, [])
            dt_list = datetime_fields.get(model_name, [])
            m2m_list = m2m_fields.get(model_name, [])

            for item in items:
                pk = item.get('pk')
                fields = dict(item['fields'])

                m2m_data = {}
                for m2m in m2m_list:
                    if m2m in fields:
                        m2m_data[m2m] = fields.pop(m2m)

                for fk in fk_list:
                    if fk in fields:
                        val = fields[fk]
                        if isinstance(val, dict):
                            fields[f'{fk}_id'] = val.get('pk')
                        elif isinstance(val, list):
                            fields[f'{fk}_id'] = val[0].get('pk') if val else None
                        else:
                            fields[f'{fk}_id'] = val
                        del fields[fk]

                for dt in dt_list:
                    if dt in fields and fields[dt] is None:
                        fields.pop(dt, None)

                try:
                    obj, created = model.objects.update_or_create(pk=pk, defaults=fields)
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                except Exception as e:
                    error_count += 1
                    self.stdout.write(self.style.WARNING(f'Xato [{model_name} pk={pk}]: {e}'))

            db_count = model.objects.count()
            self.stdout.write(self.style.SUCCESS(f'{model_name}: {len(items)} ta (DB: {db_count})'))

        self.stdout.write(self.style.SUCCESS(
            f'\n=== TUGADI ===\n'
            f'Yaratilgan: {created_count}\n'
            f'Yangilangan: {updated_count}\n'
            f'Xatolar: {error_count}\n'
            f'Jami: {created_count + updated_count}'
        ))
        self.stdout.write(self.style.SUCCESS(f'Users: {User.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Xodimlar: {Xodim.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'BonusRecord: {BonusRecord.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'JarimaRecord: {JarimaRecord.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'OzgartirishTarixi: {OzgartirishTarixi.objects.count()}'))
        self.stdout.write(self.style.SUCCESS(f'Notification: {Notification.objects.count()}'))
