import json
import os
import re
from datetime import datetime
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Sum

from main.models import Xodim


# "Bonus pulidan 100,000 so'm yechildi. Sabab: ..."
PUL_RE = re.compile(r"(?i)\b(bonus|jarima)\s+pulidan\s+([\d][\d.,]*)\s+so[’']?m\s+yechildi")
# "Bonus balldan 5 ball yechildi. Sabab: ..."
BALL_RE = re.compile(r"(?i)\b(bonus|jarima)\s+balldan\s+(\d+)\s+ball\s+yechildi")
# "Bonusdan yechildi: 5 ball, 100000 so'm. Sabab: ..." (manfiy = qaytarish)
REYTING_RE = re.compile(r"(?i)\b(bonusdan|jarimadan)\s+yechildi\s*:\s*(-?\d+)\s+ball,\s*(-?[\d][\d.,]*)\s+so[’']?m")


def parse_money(s):
    return Decimal(str(s).replace(',', '').replace(' ', ''))


def parse_sabab(sabab):
    """History matnidan yechilgan qiymatlarni qaytaradi."""
    b_pul = Decimal('0')
    j_pul = Decimal('0')
    b_ball = 0
    j_ball = 0

    m = PUL_RE.search(sabab)
    if m:
        if m.group(1).lower() == 'bonus':
            b_pul += parse_money(m.group(2))
        else:
            j_pul += parse_money(m.group(2))

    m = BALL_RE.search(sabab)
    if m:
        if m.group(1).lower() == 'bonus':
            b_ball += int(m.group(2))
        else:
            j_ball += int(m.group(2))

    m = REYTING_RE.search(sabab)
    if m:
        if m.group(1).lower() == 'bonusdan':
            b_ball += int(m.group(2))
            b_pul += parse_money(m.group(3))
        else:
            j_ball += int(m.group(2))
            j_pul += parse_money(m.group(3))

    return b_pul, j_pul, b_ball, j_ball


def dump_cutoff_id():
    """Eski dump faylidagi eng katta tarix id si (shundan keyingi yechishlar yo'qolgan bo'lishi mumkin)."""
    fayl = os.path.join('main', 'fixtures', 'dumpdata.json')
    if not os.path.exists(fayl):
        return None
    with open(fayl, encoding='utf-8') as f:
        data = json.load(f)
    ids = [d['pk'] for d in data if d['model'] == 'main.ozgartirishtarixi']
    return max(ids) if ids else None


class Command(BaseCommand):
    help = (
        "Deploy paytida init_data eski dump bilan ustiga yozib qo'ygan "
        "yechilgan pul/ball va bonus/jarima yig'indilarini qayta tiklaydi."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply', action='store_true',
            help="O'zgarishlarni bazaga yozadi (bo'lmasa faqat ko'rsatadi)",
        )
        parser.add_argument(
            '--only', type=int, default=None,
            help="Faqat bitta xodim id si (masalan: --only 12)",
        )
        parser.add_argument(
            '--from-id', type=int, default=None,
            help="Shu tarix id sidan boshlab yechishlarni qo'shadi "
                 "(standart: dump faylidagi eng katta tarix id si)",
        )
        parser.add_argument(
            '--since', type=str, default=None,
            help="Shu sanadan (YYYY-MM-DD) boshlab yechishlarni qo'shadi",
        )

    def handle(self, *args, **options):
        apply = options.get('apply')
        only_id = options.get('only')
        from_id = options.get('from_id')
        since = options.get('since')

        if from_id is None and since is None:
            from_id = dump_cutoff_id()
            self.stdout.write(self.style.NOTICE(
                f"Cutoff tarix id = {from_id} (dump faylidan aniqlangan)"
            ))

        qs = Xodim.objects.all().order_by('id')
        if only_id:
            qs = qs.filter(pk=only_id)

        jami_ozgargan = 0

        for xodim in qs:
            # Tarixdan (cutoffdan keyingi) yechilgan qiymatlarni yig'ish
            tarixlar = xodim.ozgartirish_tarixlari.all()
            if from_id is not None:
                tarixlar = tarixlar.filter(pk__gt=from_id)
            if since is not None:
                sana = datetime.strptime(since, '%Y-%m-%d').date()
                tarixlar = tarixlar.filter(sana__date__gte=sana)

            b_pul = Decimal('0')
            j_pul = Decimal('0')
            b_ball = 0
            j_ball = 0
            for t in tarixlar:
                bp, jp, bb, jb = parse_sabab(t.sabab)
                b_pul += bp
                j_pul += jp
                b_ball += bb
                j_ball += jb

            # Bonus/jarima yig'indilarini yozuvlardan qayta hisoblash
            bon = xodim.bonus_recordlari.aggregate(b=Sum('ball_miqdori'), p=Sum('pul_miqdori'))
            jar = xodim.jarima_recordlari.aggregate(b=Sum('ball_miqdori'), p=Sum('pul_miqdori'))
            bonus_ball = bon['b'] or 0
            bonus_pul = bon['p'] or Decimal('0')
            jarima_ball = jar['b'] or 0
            jarima_pul = jar['p'] or Decimal('0')

            # Yangi yechilgan qiymatlar (joriyga qo'shib hisoblaymiz)
            y_bonus_pul = xodim.bonus_pul_yechilgan + b_pul
            y_jarima_pul = xodim.jarima_pul_yechilgan + j_pul
            y_bonus_ball = xodim.bonus_ball_yechilgan + b_ball
            y_jarima_ball = xodim.jarima_ball_yechilgan + j_ball

            jami_bonus_ball = bonus_ball - y_bonus_ball - xodim.xarid_ball
            jami_jarima_ball = jarima_ball - y_jarima_ball
            reyting_ball = jami_bonus_ball - jami_jarima_ball
            reyting_pul = (bonus_pul - y_bonus_pul) - (jarima_pul - y_jarima_pul)

            taqqos = [
                ('bonus_ball', xodim.bonus_ball, bonus_ball),
                ('bonus_pul', xodim.bonus_pul, bonus_pul),
                ('jarima_ball', xodim.jarima_ball, jarima_ball),
                ('jarima_pul', xodim.jarima_pul, jarima_pul),
                ('bonus_ball_yechilgan', xodim.bonus_ball_yechilgan, y_bonus_ball),
                ('bonus_pul_yechilgan', xodim.bonus_pul_yechilgan, y_bonus_pul),
                ('jarima_ball_yechilgan', xodim.jarima_ball_yechilgan, y_jarima_ball),
                ('jarima_pul_yechilgan', xodim.jarima_pul_yechilgan, y_jarima_pul),
                ('reyting_ball', xodim.reyting_ball, reyting_ball),
                ('reyting_pul', xodim.reyting_pul, reyting_pul),
            ]

            farq = [ (nom, eski, yangi) for nom, eski, yangi in taqqos if eski != yangi ]
            if not farq:
                continue

            jami_ozgargan += 1
            self.stdout.write(self.style.WARNING(
                f"\n[{xodim.id}] {xodim.ism} {xodim.familya}"
            ))
            for nom, eski, yangi in farq:
                self.stdout.write(f"  {nom}: {eski}  ->  {yangi}")

            if apply:
                xodim.bonus_ball = bonus_ball
                xodim.bonus_pul = bonus_pul
                xodim.jarima_ball = jarima_ball
                xodim.jarima_pul = jarima_pul
                xodim.bonus_ball_yechilgan = y_bonus_ball
                xodim.bonus_pul_yechilgan = y_bonus_pul
                xodim.jarima_ball_yechilgan = y_jarima_ball
                xodim.jarima_pul_yechilgan = y_jarima_pul
                xodim.reyting_ball = reyting_ball
                xodim.reyting_pul = reyting_pul
                xodim.save()

        if apply:
            self.stdout.write(self.style.SUCCESS(
                f"\nTugadi: {jami_ozgargan} ta xodim yangilandi."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(
                f"\nDry-run: {jami_ozgargan} ta xodim o'zgaradi. "
                f"Yozish uchun --apply bilan ishga tushiring."
            ))
