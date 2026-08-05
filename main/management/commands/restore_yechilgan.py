import re
from datetime import datetime, timedelta
from decimal import Decimal

from django.core.management.base import BaseCommand
from django.db.models import Sum
from django.utils import timezone

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


def default_window():
    """Standart davr: o'tgan oyning oxirgi kuni ... joriy oyning 1-kuni (31 va 1 oraliq)."""
    bugun = timezone.localdate()
    joriy_oy_1 = bugun.replace(day=1)
    oldingi_oy_oxiri = joriy_oy_1 - timedelta(days=1)
    return oldingi_oy_oxiri, joriy_oy_1


def parse_date(s):
    return datetime.strptime(s, '%Y-%m-%d').date()


class Command(BaseCommand):
    help = (
        "Deploy paytida init_data eski dump bilan ustiga yozib qo'ygan "
        "yechilgan pul/ball va bonus/jarima yig'indilarini qayta tiklaydi.\n"
        "Standart: o'tgan oy oxiri (31) va joriy oy 1-kuni oralig'idagi yechishlarni topadi."
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
            '--since', type=str, default=None,
            help="Boshlanish sanasi (YYYY-MM-DD). Standart: o'tgan oyning oxirgi kuni",
        )
        parser.add_argument(
            '--until', type=str, default=None,
            help="Tugash sanasi (YYYY-MM-DD). Standart: joriy oyning 1-kuni",
        )
        parser.add_argument(
            '--from-id', type=int, default=None,
            help="Shu tarix id sidan boshlab yechishlarni qo'shadi (--since/--until ni e'tiborsiz qoldiradi)",
        )

    def handle(self, *args, **options):
        apply = options.get('apply')
        only_id = options.get('only')
        from_id = options.get('from_id')
        since = options.get('since')
        until = options.get('until')

        # Standart davr: 31 va 1 oraliq
        if from_id is None and since is None and until is None:
            since_d, until_d = default_window()
        else:
            since_d = parse_date(since) if since else None
            until_d = parse_date(until) if until else None

        if from_id is not None:
            self.stdout.write(self.style.NOTICE(f"Davr: tarix id > {from_id}"))
        else:
            self.stdout.write(self.style.NOTICE(
                f"Davr: {since_d} ... {until_d}"
            ))

        qs = Xodim.objects.all().order_by('id')
        if only_id:
            qs = qs.filter(pk=only_id)

        jami_ozgargan = 0

        for xodim in qs:
            # Tarixdan (davrdagi) yechilgan qiymatlarni yig'ish.
            # Sana solishtirish Pythonda bajariladi (SQLite'da __date ishonchli emas).
            tarixlar = xodim.ozgartirish_tarixlari.all()
            if from_id is not None:
                tarixlar = tarixlar.filter(pk__gt=from_id)

            b_pul = Decimal('0')
            j_pul = Decimal('0')
            b_ball = 0
            j_ball = 0
            for t in tarixlar:
                if t.sana:
                    sana_d = timezone.localtime(t.sana).date()
                else:
                    sana_d = None
                if since_d is not None and (sana_d is None or sana_d < since_d):
                    continue
                if until_d is not None and (sana_d is None or sana_d > until_d):
                    continue
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
