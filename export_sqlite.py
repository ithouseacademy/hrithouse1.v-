import sqlite3
import json
from datetime import datetime

conn = sqlite3.connect('db.sqlite3')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

data = []

# Model mapping: sqlite table -> (django model, app_label)
model_map = {
    'auth_user': 'auth.user',
    'main_bonussabab': 'main.bonussabab',
    'main_jarimasabab': 'main.jarimasabab',
    'main_xodim': 'main.xodim',
    'main_bonusrecord': 'main.bonusrecord',
    'main_jarimarecord': 'main.jarimarecord',
    'main_ozgartirishtarixi': 'main.ozgartirishtarixi',
    'main_category': 'main.category',
    'main_product': 'main.product',
    'main_productorder': 'main.productorder',
    'main_pointtransaction': 'main.pointtransaction',
    'main_notification': 'main.notification',
    'main_pushsubscription': 'main.pushsubscription',
}

# Field mapping per model
field_maps = {
    'auth_user': {
        'id': 'pk',
        'username': 'username',
        'password': 'password',
        'email': 'email',
        'first_name': 'first_name',
        'last_name': 'last_name',
        'is_staff': 'is_staff',
        'is_active': 'is_active',
        'is_superuser': 'is_superuser',
        'last_login': 'last_login',
        'date_joined': 'date_joined',
    },
    'main_bonussabab': {
        'id': 'pk',
        'nom': 'nom',
        'pul_miqdori': 'pul_miqdori',
        'ball_miqdori': 'ball_miqdori',
        'active': 'active',
        'created_at': 'created_at',
    },
    'main_jarimasabab': {
        'id': 'pk',
        'nom': 'nom',
        'pul_miqdori': 'pul_miqdori',
        'ball_miqdori': 'ball_miqdori',
        'active': 'active',
        'created_at': 'created_at',
    },
    'main_xodim': {
        'id': 'pk',
        'user_id': ('user', 'auth.user'),
        'ism': 'ism',
        'familya': 'familya',
        'telefon': 'telefon',
        'lavozim': 'lavozim',
        'active': 'active',
        'rasm': 'rasm',
        'bonus_ball': 'bonus_ball',
        'bonus_pul': 'bonus_pul',
        'bonus_ball_yechilgan': 'bonus_ball_yechilgan',
        'bonus_pul_yechilgan': 'bonus_pul_yechilgan',
        'jarima_ball': 'jarima_ball',
        'jarima_pul': 'jarima_pul',
        'jarima_ball_yechilgan': 'jarima_ball_yechilgan',
        'jarima_pul_yechilgan': 'jarima_pul_yechilgan',
        'reyting_ball': 'reyting_ball',
        'reyting_pul': 'reyting_pul',
        'xarid_ball': 'xarid_ball',
        'created_at': 'created_at',
        'updated_at': 'updated_at',
    },
    'main_bonusrecord': {
        'id': 'pk',
        'xodim_id': ('xodim', 'main.xodim'),
        'sabab_id': ('sabab', 'main.bonussabab'),
        'pul_miqdori': 'pul_miqdori',
        'ball_miqdori': 'ball_miqdori',
        'izoh': 'izoh',
        'created_by_id': ('created_by', 'auth.user'),
        'sana': 'sana',
    },
    'main_jarimarecord': {
        'id': 'pk',
        'xodim_id': ('xodim', 'main.xodim'),
        'sabab_id': ('sabab', 'main.jarimasabab'),
        'pul_miqdori': 'pul_miqdori',
        'ball_miqdori': 'ball_miqdori',
        'izoh': 'izoh',
        'created_by_id': ('created_by', 'auth.user'),
        'sana': 'sana',
    },
    'main_ozgartirishtarixi': {
        'id': 'pk',
        'xodim_id': ('xodim', 'main.xodim'),
        'admin_id': ('admin', 'auth.user'),
        'sabab': 'sabab',
        'sana': 'sana',
        'eski_bonus_ball': 'eski_bonus_ball',
        'eski_bonus_pul': 'eski_bonus_pul',
        'eski_jarima_ball': 'eski_jarima_ball',
        'eski_jarima_pul': 'eski_jarima_pul',
        'yangi_bonus_ball': 'yangi_bonus_ball',
        'yangi_bonus_pul': 'yangi_bonus_pul',
        'yangi_jarima_ball': 'yangi_jarima_ball',
        'yangi_jarima_pul': 'yangi_jarima_pul',
    },
    'main_category': {
        'id': 'pk',
        'name': 'name',
        'order': 'order',
    },
    'main_product': {
        'id': 'pk',
        'name': 'name',
        'description': 'description',
        'price_points': 'price_points',
        'stock': 'stock',
        'is_active': 'is_active',
        'category_id': ('category', 'main.category'),
        'is_coming_soon': 'is_coming_soon',
        'created_at': 'created_at',
    },
    'main_notification': {
        'id': 'pk',
        'user_id': ('user', 'auth.user'),
        'title': 'title',
        'message': 'message',
        'is_read': 'is_read',
        'created_at': 'created_at',
    },
}

# Columns to skip (not in Django model or auto-generated)
skip_columns = {
    'auth_user': ['user_permissions'],
    'main_xodim': ['eski_bonus_ball_yechilgan', 'eski_bonus_pul_yechilgan', 'eski_jarima_ball_yechilgan', 'eski_jarima_pul_yechilgan', 'yangi_bonus_ball_yechilgan', 'yangi_bonus_pul_yechilgan', 'yangi_jarima_ball_yechilgan', 'yangi_jarima_pul_yechilgan'],
}


def convert_value(val, field_type):
    if val is None:
        return None
    if isinstance(field_type, tuple):
        fk_field, fk_model = field_type
        if val == '' or val is None:
            return None
        return {'model': fk_model, 'pk': int(val)}
    if field_type == 'pk':
        return int(val)
    if field_type in ('pul_miqdori', 'bonus_pul', 'jarima_pul',
                       'eski_bonus_pul', 'eski_jarima_pul',
                       'yangi_bonus_pul', 'yangi_jarima_pul',
                       'bonus_pul_yechilgan', 'jarima_pul_yechilgan',
                       'reyting_pul'):
        return float(val)
    if field_type in ('ball_miqdori', 'bonus_ball', 'jarima_ball',
                       'eski_bonus_ball', 'eski_jarima_ball',
                       'yangi_bonus_ball', 'yangi_jarima_ball',
                       'bonus_ball_yechilgan', 'jarima_ball_yechilgan',
                       'reyting_ball', 'xarid_ball',
                       'price_points', 'stock', 'order'):
        return int(val)
    if field_type in ('active', 'is_active', 'is_staff', 'is_superuser',
                       'is_read', 'is_coming_soon'):
        return bool(val)
    if field_type in ('last_login', 'date_joined', 'sana', 'created_at',
                       'updated_at', 'approved_at', 'rejected_at'):
        if val and val != '':
            return str(val)
        return None
    if field_type == 'rasm':
        if val and val != '':
            return str(val)
        return None
    return str(val)


# Export order
export_order = [
    'auth_user',
    'main_bonussabab',
    'main_jarimasabab',
    'main_xodim',
    'main_bonusrecord',
    'main_jarimarecord',
    'main_ozgartirishtarixi',
    'main_category',
    'main_product',
    'main_notification',
]

for table in export_order:
    django_model = model_map.get(table)
    field_map = field_maps.get(table)
    if not django_model or not field_map:
        continue

    cursor.execute(f'SELECT * FROM [{table}]')
    rows = cursor.fetchall()
    print(f'{table}: {len(rows)} yozuv export qilinmoqda...')

    for row in rows:
        fields = {}
        for col_name in row.keys():
            if col_name in ('id',):
                continue
            if table in skip_columns and col_name in skip_columns[table]:
                continue

            if col_name in field_map:
                field_spec = field_map[col_name]
                if isinstance(field_spec, tuple):
                    fields[field_spec[0]] = convert_value(row[col_name], field_spec)
                else:
                    fields[field_spec] = convert_value(row[col_name], field_spec)

        entry = {
            'model': django_model,
            'pk': int(row['id']),
            'fields': fields,
        }
        data.append(entry)

conn.close()

output_path = 'main/fixtures/dumpdata.json'
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2, default=str)

print(f'\nJAMI: {len(data)} yozuv export qilindi -> {output_path}')
