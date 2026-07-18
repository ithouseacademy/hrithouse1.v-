from django.db import models
from django.contrib.auth.models import User
from django.db.models import Sum
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from datetime import datetime, timedelta
from django.utils import timezone
from decimal import Decimal

# main/models.py - OzgartirishTarixi modeliga qo'shing


class Category(models.Model):
    name = models.CharField(max_length=255)
    order = models.PositiveIntegerField(default=0, help_text="Tartib raqami")

    class Meta:
        ordering = ['order', 'name']
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, default='')
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    price_points = models.IntegerField(help_text="Kerakli ball miqdori")
    stock = models.PositiveIntegerField(default=0, help_text="Ombordagi soni")
    is_active = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products', verbose_name="Kategoriya")
    is_coming_soon = models.BooleanField(default=False, help_text="Tez orada keladi")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"

    def __str__(self):
        return self.name


class ProductOrder(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shop_orders')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='orders')
    points_spent = models.IntegerField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_at = models.DateTimeField(null=True, blank=True)
    reject_reason = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"


class PointTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('PURCHASE', 'Purchase'),
        ('REFUND', 'Refund'),
        ('REWARD', 'Reward'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='point_transactions')
    amount = models.IntegerField()
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    description = models.TextField(blank=True, default='')
    order = models.ForeignKey(ProductOrder, on_delete=models.SET_NULL, null=True, blank=True, related_name='transactions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Ball tranzaksiyasi"
        verbose_name_plural = "Ball tranzaksiyalari"

    def __str__(self):
        return f"{self.user.username} - {self.get_transaction_type_display()} - {self.amount} ball"


class OzgartirishTarixi(models.Model):
    """Xodim ma'lumotlarini o'zgartirish tarixi"""
    xodim = models.ForeignKey('Xodim', on_delete=models.CASCADE, related_name='ozgartirish_tarixlari')
    admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    sabab = models.TextField()
    sana = models.DateTimeField(auto_now_add=True)
    
    # Eski qiymatlar
    eski_bonus_ball = models.IntegerField(default=0)
    eski_bonus_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    eski_jarima_ball = models.IntegerField(default=0)
    eski_jarima_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # YANGI QO'SHILGAN MAYDONLAR
    eski_bonus_ball_yechilgan = models.IntegerField(default=0)
    eski_bonus_pul_yechilgan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    eski_jarima_ball_yechilgan = models.IntegerField(default=0)
    eski_jarima_pul_yechilgan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # Yangi qiymatlar
    yangi_bonus_ball = models.IntegerField(default=0)
    yangi_bonus_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    yangi_jarima_ball = models.IntegerField(default=0)
    yangi_jarima_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    # YANGI QO'SHILGAN MAYDONLAR
    yangi_bonus_ball_yechilgan = models.IntegerField(default=0)
    yangi_bonus_pul_yechilgan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    yangi_jarima_ball_yechilgan = models.IntegerField(default=0)
    yangi_jarima_pul_yechilgan = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    
    class Meta:
        ordering = ['-sana']
        verbose_name = "O'zgartirish tarixi"
        verbose_name_plural = "O'zgartirish tarixlari"
    
    def __str__(self):
        return f"{self.xodim} - {self.sana.strftime('%d.%m.%Y %H:%M')}"
    
    
class BonusSabab(models.Model):
    """Bonus sabablari"""
    nom = models.CharField(max_length=200)
    pul_miqdori = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ball_miqdori = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} | {self.pul_miqdori} so'm | {self.ball_miqdori} ball"
    
    class Meta:
        verbose_name = "Bonus sababi"
        verbose_name_plural = "Bonus sabablari"


class JarimaSabab(models.Model):
    """Jarima sabablari"""
    nom = models.CharField(max_length=200)
    pul_miqdori = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ball_miqdori = models.IntegerField(default=0)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.nom} | {self.pul_miqdori} so'm | {self.ball_miqdori} ball"
    
    class Meta:
        verbose_name = "Jarima sababi"
        verbose_name_plural = "Jarima sabablari"


class Xodim(models.Model):
    """Xodim modeli - to'liq versiya"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='xodim')
    ism = models.CharField(max_length=100)
    familya = models.CharField(max_length=100)
    telefon = models.CharField(max_length=20)
    lavozim = models.CharField(max_length=100, blank=True, default='')
    active = models.BooleanField(default=True)
    
    # Rasm maydoni
    rasm = models.ImageField(upload_to='xodim_rasmlari/', null=True, blank=True)
    
    # ============================================================
    # BONUS MAYDONLARI
    # ============================================================
    # Umumiy bonus (hech qachon kamaymaydi)
    bonus_ball = models.IntegerField(default=0, help_text="Umumiy bonus ball")
    bonus_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Umumiy bonus pul")
    
    # Yechilgan bonus (faqat shu o'zgaradi)
    bonus_ball_yechilgan = models.IntegerField(default=0, help_text="Yechilgan bonus ball")
    bonus_pul_yechilgan = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Yechilgan bonus pul")
    
    # ============================================================
    # JARIMA MAYDONLARI
    # ============================================================
    # Umumiy jarima (hech qachon kamaymaydi)
    jarima_ball = models.IntegerField(default=0, help_text="Umumiy jarima ball")
    jarima_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Umumiy jarima pul")
    
    # Yechilgan jarima (faqat shu o'zgaradi)
    jarima_ball_yechilgan = models.IntegerField(default=0, help_text="Yechilgan jarima ball")
    jarima_pul_yechilgan = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Yechilgan jarima pul")
    
    # ============================================================
    # REYTING MAYDONLARI
    # ============================================================
    reyting_ball = models.IntegerField(default=0, help_text="Sof reyting ball (bonus - jarima)")
    reyting_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0, help_text="Sof reyting pul")
    
    # Xarid uchun sarflangan ball (shop)
    xarid_ball = models.IntegerField(default=0, help_text="Shopda sarflangan ball")
    
    # Vaqt maydonlari
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # ============================================================
    # PROPERTY METHODLAR - MAVJUD QIYMATLAR
    # ============================================================
    
    @property
    def jami_bonus_ball(self):
        """Mavjud bonus ball (umumiy - yechilgan - xarid)"""
        return self.bonus_ball - self.bonus_ball_yechilgan - self.xarid_ball
    
    @property
    def jami_bonus_pul(self):
        """Mavjud bonus pul (umumiy - yechilgan)"""
        return self.bonus_pul - self.bonus_pul_yechilgan
    
    @property
    def jami_jarima_ball(self):
        """Mavjud jarima ball (umumiy - yechilgan)"""
        return self.jarima_ball - self.jarima_ball_yechilgan
    
    @property
    def jami_jarima_pul(self):
        """Mavjud jarima pul (umumiy - yechilgan)"""
        return self.jarima_pul - self.jarima_pul_yechilgan
    
    @property
    def sof_reyting_ball(self):
        """Sof reyting ball (mavjud bonus - mavjud jarima)"""
        return self.jami_bonus_ball - self.jami_jarima_ball
    
    @property
    def sof_reyting_pul(self):
        """Sof reyting pul (mavjud bonus pul - mavjud jarima pul)"""
        return self.jami_bonus_pul - self.jami_jarima_pul
    
    # ============================================================
    # YECHISH METHODLARI
    # ============================================================
    
    def bonus_ball_yechish(self, miqdor):
        """Bonus ballni yechish"""
        if miqdor <= self.jami_bonus_ball and miqdor > 0:
            self.bonus_ball_yechilgan += miqdor
            self.reyting_ball = self.jami_bonus_ball - self.jami_jarima_ball
            self.save(update_fields=['bonus_ball_yechilgan', 'reyting_ball'])
            return True
        return False
    
    def bonus_pul_yechish(self, miqdor):
        """Bonus pulni yechish"""
        if miqdor <= self.jami_bonus_pul and miqdor > 0:
            self.bonus_pul_yechilgan += miqdor
            self.reyting_pul = self.jami_bonus_pul - self.jami_jarima_pul
            self.save(update_fields=['bonus_pul_yechilgan', 'reyting_pul'])
            return True
        return False
    
    def jarima_ball_yechish(self, miqdor):
        """Jarima ballni yechish"""
        if miqdor <= self.jami_jarima_ball and miqdor > 0:
            self.jarima_ball_yechilgan += miqdor
            self.reyting_ball = self.jami_bonus_ball - self.jami_jarima_ball
            self.save(update_fields=['jarima_ball_yechilgan', 'reyting_ball'])
            return True
        return False
    
    def jarima_pul_yechish(self, miqdor):
        """Jarima pulni yechish"""
        if miqdor <= self.jami_jarima_pul and miqdor > 0:
            self.jarima_pul_yechilgan += miqdor
            self.reyting_pul = self.jami_bonus_pul - self.jami_jarima_pul
            self.save(update_fields=['jarima_pul_yechilgan', 'reyting_pul'])
            return True
        return False
    
    # ============================================================
    # YANGILASH METHODLARI
    # ============================================================
    
    def update_reyting(self):
        """Reytingni yangilash"""
        self.reyting_ball = self.jami_bonus_ball - self.jami_jarima_ball
        self.reyting_pul = self.jami_bonus_pul - self.jami_jarima_pul
        self.save(update_fields=['reyting_ball', 'reyting_pul'])
    
    def update_from_records(self):
        """BonusRecord va JarimaRecord dan jami qiymatlarni hisoblab yangilaydi"""
        # Eski yechilgan qiymatlarni saqlash
        eski_bonus_ball_yechilgan = self.bonus_ball_yechilgan
        eski_bonus_pul_yechilgan = self.bonus_pul_yechilgan
        eski_jarima_ball_yechilgan = self.jarima_ball_yechilgan
        eski_jarima_pul_yechilgan = self.jarima_pul_yechilgan
        
        # Bonuslarni yig'ish
        bonus_agg = self.bonus_recordlari.aggregate(
            jami_ball=Sum('ball_miqdori'),
            jami_pul=Sum('pul_miqdori')
        )
        self.bonus_ball = bonus_agg['jami_ball'] or 0
        self.bonus_pul = bonus_agg['jami_pul'] or Decimal('0')
        
        # Jarimalarni yig'ish
        jarima_agg = self.jarima_recordlari.aggregate(
            jami_ball=Sum('ball_miqdori'),
            jami_pul=Sum('pul_miqdori')
        )
        self.jarima_ball = jarima_agg['jami_ball'] or 0
        self.jarima_pul = jarima_agg['jami_pul'] or Decimal('0')
        
        # Yechilgan qiymatlarni qayta tiklash
        self.bonus_ball_yechilgan = eski_bonus_ball_yechilgan
        self.bonus_pul_yechilgan = eski_bonus_pul_yechilgan
        self.jarima_ball_yechilgan = eski_jarima_ball_yechilgan
        self.jarima_pul_yechilgan = eski_jarima_pul_yechilgan
        
        # Reytingni yangilash
        self.reyting_ball = self.jami_bonus_ball - self.jami_jarima_ball
        self.reyting_pul = self.jami_bonus_pul - self.jami_jarima_pul
        
        self.save(update_fields=[
            'bonus_ball', 'bonus_pul',
            'jarima_ball', 'jarima_pul',
            'bonus_ball_yechilgan', 'bonus_pul_yechilgan',
            'jarima_ball_yechilgan', 'jarima_pul_yechilgan',
            'reyting_ball', 'reyting_pul',
            'xarid_ball'
        ])
    
    def __str__(self):
        return f"{self.ism} {self.familya}"
    
    class Meta:
        ordering = ['-reyting_ball']
        verbose_name = "Xodim"
        verbose_name_plural = "Xodimlar"


class BonusRecord(models.Model):
    """Bonus yozuvlari"""
    xodim = models.ForeignKey(Xodim, on_delete=models.CASCADE, related_name='bonus_recordlari')
    sabab = models.ForeignKey(BonusSabab, on_delete=models.SET_NULL, null=True, blank=True)
    pul_miqdori = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ball_miqdori = models.IntegerField(default=0)
    sana = models.DateTimeField(auto_now_add=True)
    izoh = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-sana']
        verbose_name = "Bonus yozuvi"
        verbose_name_plural = "Bonus yozuvlari"
    
    def __str__(self):
        return f"{self.xodim} - +{self.ball_miqdori} ball / {self.pul_miqdori} so'm"


class JarimaRecord(models.Model):
    """Jarima yozuvlari"""
    xodim = models.ForeignKey(Xodim, on_delete=models.CASCADE, related_name='jarima_recordlari')
    sabab = models.ForeignKey(JarimaSabab, on_delete=models.SET_NULL, null=True, blank=True)
    pul_miqdori = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    ball_miqdori = models.IntegerField(default=0)
    sana = models.DateTimeField(auto_now_add=True)
    izoh = models.TextField(blank=True, default='')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-sana']
        verbose_name = "Jarima yozuvi"
        verbose_name_plural = "Jarima yozuvlari"
    
    def __str__(self):
        return f"{self.xodim} - -{self.ball_miqdori} ball / {self.pul_miqdori} so'm"


class Reyting(models.Model):
    """Davrlar bo'yicha reyting"""
    DAVR_TANLOVLARI = [
        ('kunlik', 'Kunlik'),
        ('haftalik', 'Haftalik'),
        ('oylik', 'Oylik'),
        ('yillik', 'Yillik'),
    ]
    
    xodim = models.ForeignKey(Xodim, on_delete=models.CASCADE, related_name='reytinglari')
    davr = models.CharField(max_length=20, choices=DAVR_TANLOVLARI)
    bonus_ball = models.IntegerField(default=0)
    bonus_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    jarima_ball = models.IntegerField(default=0)
    jarima_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    reyting_ball = models.IntegerField(default=0)
    reyting_pul = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    sana = models.DateField(default=timezone.now)
    
    def save(self, *args, **kwargs):
        if not self.sana:
            self.sana = timezone.now().date()
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ['xodim', 'davr', 'sana']
        ordering = ['-reyting_ball']
    
    def __str__(self):
        return f"{self.xodim} - {self.get_davr_display()} - {self.reyting_ball} ball"


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=255)
    message = models.TextField()
    url = models.CharField(max_length=500, blank=True, default='')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Bildirishnoma"
        verbose_name_plural = "Bildirishnomalar"

    def __str__(self):
        return f"{self.user.username} - {self.title}"


class PushSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='push_subscriptions')
    endpoint = models.TextField()
    p256dh_key = models.TextField(verbose_name="P256DH Key")
    auth_key = models.TextField(verbose_name="Auth Key")
    user_agent = models.CharField(max_length=500, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Push obuna"
        verbose_name_plural = "Push obunalar"

    def __str__(self):
        return f"{self.user.username} - {self.created_at.strftime('%d.%m.%Y')}"


# ============================================================
# SIGNALLAR - Bonus va Jarima qo'shilganda avtomatik yangilash
# ============================================================

@receiver(post_save, sender=BonusRecord)
def update_xodim_after_bonus_save(sender, instance, created, **kwargs):
    """Bonus qo'shilganda xodim ma'lumotlarini yangilaydi"""
    instance.xodim.update_from_records()


@receiver(post_delete, sender=BonusRecord)
def update_xodim_after_bonus_delete(sender, instance, **kwargs):
    """Bonus o'chirilganda xodim ma'lumotlarini yangilaydi"""
    instance.xodim.update_from_records()


@receiver(post_save, sender=JarimaRecord)
def update_xodim_after_jarima_save(sender, instance, created, **kwargs):
    """Jarima qo'shilganda xodim ma'lumotlarini yangilaydi"""
    instance.xodim.update_from_records()


@receiver(post_delete, sender=JarimaRecord)
def update_xodim_after_jarima_delete(sender, instance, **kwargs):
    """Jarima o'chirilganda xodim ma'lumotlarini yangilaydi"""
    instance.xodim.update_from_records()