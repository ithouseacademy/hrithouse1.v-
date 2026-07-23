from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.conf import settings
from .models import (
    Xodim, BonusRecord, JarimaRecord, 
    BonusSabab, JarimaSabab, 
    OzgartirishTarixi, Reyting,
    Category, Product, ProductOrder, PointTransaction,
    Notification, PushSubscription, SiteSettings
)


@admin.register(BonusSabab)
class BonusSababAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom', 'pul_miqdori', 'ball_miqdori', 'active', 'created_at']
    list_filter = ['active']
    search_fields = ['nom']
    list_editable = ['pul_miqdori', 'ball_miqdori', 'active']
    list_per_page = 20
    ordering = ['-ball_miqdori']


@admin.register(JarimaSabab)
class JarimaSababAdmin(admin.ModelAdmin):
    list_display = ['id', 'nom', 'pul_miqdori', 'ball_miqdori', 'active', 'created_at']
    list_filter = ['active']
    search_fields = ['nom']
    list_editable = ['pul_miqdori', 'ball_miqdori', 'active']
    list_per_page = 20
    ordering = ['-ball_miqdori']


@admin.register(Xodim)
class XodimAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'ism', 'familya', 'telefon', 'lavozim', 
        'bonus_ball', 'jarima_ball', 'reyting_ball', 
        'jami_bonus_pul_display', 'jami_jarima_pul_display', 'active'
    ]
    list_filter = ['active', 'lavozim', 'created_at']
    search_fields = ['ism', 'familya', 'telefon', 'lavozim']
    readonly_fields = [
        'bonus_ball', 'bonus_pul', 'jarima_ball', 'jarima_pul',
        'reyting_ball', 'reyting_pul', 'created_at', 'updated_at'
    ]
    list_per_page = 20
    ordering = ['-reyting_ball']
    
    fieldsets = (
        ('Shaxsiy ma\'lumotlar', {
            'fields': ('user', 'ism', 'familya', 'telefon', 'lavozim', 'rasm', 'active')
        }),
        ('Bonus ma\'lumotlari', {
            'fields': ('bonus_ball', 'bonus_pul', 'bonus_pul_yechilgan'),
            'classes': ('collapse',)
        }),
        ('Jarima ma\'lumotlari', {
            'fields': ('jarima_ball', 'jarima_pul', 'jarima_pul_yechilgan'),
            'classes': ('collapse',)
        }),
        ('Reyting', {
            'fields': ('reyting_ball', 'reyting_pul'),
            'classes': ('collapse',)
        }),
        ('Vaqt', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def jami_bonus_pul_display(self, obj):
        """Mavjud bonus pul"""
        value = obj.jami_bonus_pul
        color = 'green' if value >= 0 else 'red'
        return format_html('<span style="color: {};">{:,.0f} so\'m</span>', color, value)
    jami_bonus_pul_display.short_description = "Mavjud bonus"
    
    def jami_jarima_pul_display(self, obj):
        """Mavjud jarima pul"""
        value = obj.jami_jarima_pul
        color = 'red' if value > 0 else 'green'
        return format_html('<span style="color: {};">{:,.0f} so\'m</span>', color, value)
    jami_jarima_pul_display.short_description = "Mavjud jarima"
    
    def get_readonly_fields(self, request, obj=None):
        if obj:  # Tahrirlashda
            return self.readonly_fields
        return []  # Yaratishda


@admin.register(BonusRecord)
class BonusRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'xodim_link', 'sabab', 'pul_miqdori', 'ball_miqdori', 
        'sana_formati', 'created_by', 'izoh_qisqa'
    ]
    list_filter = ['sana', 'sabab', 'created_by']
    search_fields = ['xodim__ism', 'xodim__familya', 'xodim__telefon', 'izoh']
    date_hierarchy = 'sana'
    readonly_fields = ['sana', 'created_by']
    list_per_page = 20
    autocomplete_fields = ['xodim', 'sabab']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('xodim', 'sabab')
        }),
        ('Miqdorlar', {
            'fields': ('pul_miqdori', 'ball_miqdori')
        }),
        ('Qo\'shimcha', {
            'fields': ('izoh', 'sana', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def xodim_link(self, obj):
        return format_html(
            '<a href="/admin/main/xodim/{}/change/" target="_blank">{}</a>',
            obj.xodim.id, obj.xodim.ism
        )
    xodim_link.short_description = "Xodim"
    
    def sana_formati(self, obj):
        return obj.sana.strftime('%d.%m.%Y %H:%M')
    sana_formati.short_description = "Sana"
    
    def izoh_qisqa(self, obj):
        return obj.izoh[:50] + '...' if len(obj.izoh) > 50 else obj.izoh
    izoh_qisqa.short_description = "Izoh"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(JarimaRecord)
class JarimaRecordAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'xodim_link', 'sabab', 'pul_miqdori', 'ball_miqdori', 
        'sana_formati', 'created_by', 'izoh_qisqa'
    ]
    list_filter = ['sana', 'sabab', 'created_by']
    search_fields = ['xodim__ism', 'xodim__familya', 'xodim__telefon', 'izoh']
    date_hierarchy = 'sana'
    readonly_fields = ['sana', 'created_by']
    list_per_page = 20
    autocomplete_fields = ['xodim', 'sabab']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('xodim', 'sabab')
        }),
        ('Miqdorlar', {
            'fields': ('pul_miqdori', 'ball_miqdori')
        }),
        ('Qo\'shimcha', {
            'fields': ('izoh', 'sana', 'created_by'),
            'classes': ('collapse',)
        }),
    )
    
    def xodim_link(self, obj):
        return format_html(
            '<a href="/admin/main/xodim/{}/change/" target="_blank">{}</a>',
            obj.xodim.id, obj.xodim.ism
        )
    xodim_link.short_description = "Xodim"
    
    def sana_formati(self, obj):
        return obj.sana.strftime('%d.%m.%Y %H:%M')
    sana_formati.short_description = "Sana"
    
    def izoh_qisqa(self, obj):
        return obj.izoh[:50] + '...' if len(obj.izoh) > 50 else obj.izoh
    izoh_qisqa.short_description = "Izoh"
    
    def save_model(self, request, obj, form, change):
        if not obj.created_by:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)


@admin.register(Reyting)
class ReytingAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'xodim_link', 'davr', 'reyting_ball', 'reyting_pul', 'sana_formati'
    ]
    list_filter = ['davr', 'sana']
    search_fields = ['xodim__ism', 'xodim__familya']
    date_hierarchy = 'sana'
    list_per_page = 20
    autocomplete_fields = ['xodim']
    
    fieldsets = (
        ('Asosiy ma\'lumotlar', {
            'fields': ('xodim', 'davr')
        }),
        ('Reyting', {
            'fields': ('reyting_ball', 'reyting_pul')
        }),
        ('Vaqt', {
            'fields': ('sana',)
        }),
    )
    
    def xodim_link(self, obj):
        return format_html(
            '<a href="/admin/main/xodim/{}/change/" target="_blank">{}</a>',
            obj.xodim.id, obj.xodim.ism
        )
    xodim_link.short_description = "Xodim"
    
    def sana_formati(self, obj):
        return obj.sana.strftime('%d.%m.%Y')
    sana_formati.short_description = "Sana"
    
    def save_model(self, request, obj, form, change):
        if not obj.sana:
            obj.sana = timezone.now().date()
        super().save_model(request, obj, form, change)


@admin.register(OzgartirishTarixi)
class OzgartirishTarixiAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'xodim_link', 'admin_link', 'sana_formati', 'qisqa_sabab'
    ]
    list_filter = ['sana']
    search_fields = ['xodim__ism', 'xodim__familya', 'sabab']
    readonly_fields = ['sana']
    list_per_page = 20
    
    fieldsets = (
        ('Asosiy', {
            'fields': ('xodim', 'admin', 'sabab', 'sana')
        }),
        ('Eski qiymatlar', {
            'fields': ('eski_bonus_ball', 'eski_bonus_pul', 'eski_jarima_ball', 'eski_jarima_pul'),
            'classes': ('collapse',)
        }),
        ('Yangi qiymatlar', {
            'fields': ('yangi_bonus_ball', 'yangi_bonus_pul', 'yangi_jarima_ball', 'yangi_jarima_pul'),
            'classes': ('collapse',)
        }),
    )
    
    def xodim_link(self, obj):
        return format_html(
            '<a href="/admin/main/xodim/{}/change/" target="_blank">{}</a>',
            obj.xodim.id, obj.xodim.ism
        )
    xodim_link.short_description = "Xodim"
    
    def admin_link(self, obj):
        if obj.admin:
            return format_html(
                '<a href="/admin/auth/user/{}/change/" target="_blank">{}</a>',
                obj.admin.id, obj.admin.username
            )
        return "-"
    admin_link.short_description = "Admin"
    
    def sana_formati(self, obj):
        return obj.sana.strftime('%d.%m.%Y %H:%M:%S')
    sana_formati.short_description = "Sana"
    
    def qisqa_sabab(self, obj):
        return obj.sabab[:100] + '...' if len(obj.sabab) > 100 else obj.sabab
    qisqa_sabab.short_description = "Sabab"
    
    def has_add_permission(self, request):
        """Tarixga qo'shish mumkin emas"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Tarixni o'zgartirish mumkin emas"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Tarixni o'chirish mumkin emas"""
        return False


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'order', 'product_count']
    search_fields = ['name']
    list_editable = ['order']
    list_per_page = 20
    ordering = ['order', 'name']

    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = "Mahsulotlar soni"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'category', 'price_points', 'stock', 'is_coming_soon', 'is_active', 'image_preview', 'created_at']
    list_filter = ['is_active', 'is_coming_soon', 'category', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['price_points', 'stock', 'is_coming_soon', 'is_active']
    list_per_page = 20
    ordering = ['-created_at']
    fieldsets = (
        ('Asosiy', {
            'fields': ('name', 'description', 'image', 'category', 'price_points', 'stock', 'is_active', 'is_coming_soon')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="width:50px;height:50px;object-fit:cover;border-radius:8px;" />', obj.image.url)
        return "-"
    image_preview.short_description = "Rasm"


@admin.register(ProductOrder)
class ProductOrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product_link', 'points_spent', 'status_badge', 'created_at', 'approved_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'product__name', 'reject_reason']
    readonly_fields = ['user', 'product', 'points_spent', 'created_at', 'approved_at', 'rejected_at', 'status']
    list_per_page = 20
    ordering = ['-created_at']

    def product_link(self, obj):
        url = reverse('admin:main_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.name)
    product_link.short_description = "Mahsulot"

    def status_badge(self, obj):
        colors = {'PENDING': 'orange', 'APPROVED': 'green', 'REJECTED': 'red'}
        color = colors.get(obj.status, 'gray')
        return format_html('<span style="color:{};font-weight:bold;">{}</span>', color, obj.status)
    status_badge.short_description = "Holati"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(PointTransaction)
class PointTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'amount', 'transaction_type', 'order_link', 'description', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['user__username', 'description']
    readonly_fields = ['user', 'amount', 'transaction_type', 'description', 'order', 'created_at']
    list_per_page = 20
    ordering = ['-created_at']

    def order_link(self, obj):
        if obj.order:
            url = reverse('admin:main_productorder_change', args=[obj.order.id])
            return format_html('<a href="{}">#{}</a>', url, obj.order.id)
        return "-"
    order_link.short_description = "Buyurtma"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'title', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['user__username', 'title', 'message']
    list_per_page = 20
    readonly_fields = ['user', 'title', 'message', 'url', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser


@admin.register(PushSubscription)
class PushSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'user_agent', 'created_at']
    search_fields = ['user__username', 'user_agent']
    list_per_page = 20
    readonly_fields = ['user', 'endpoint', 'p256dh_key', 'auth_key', 'user_agent', 'created_at']
    ordering = ['-created_at']

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


# Admin panel sozlamalari
admin.site.site_header = "Xodimlar Reytingi Boshqaruvi"
admin.site.site_title = "Reyting Admin"
admin.site.index_title = "Boshqaruv Paneliga Xush Kelibsiz"
admin.site.site_url = "/"


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Telegram Bot', {
            'fields': ('telegram_bot_token', 'telegram_chat_id'),
            'description': 'Telegram bot orqali xabarlar yuborish uchun sozlamalar'
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        from django.conf import settings as django_settings
        django_settings.TELEGRAM_BOT_TOKEN = obj.telegram_bot_token
        django_settings.TELEGRAM_CHAT_ID = obj.telegram_chat_id