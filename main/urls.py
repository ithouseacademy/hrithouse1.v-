# main/urls.py (to'liq versiya)

from django.urls import path
from . import views

urlpatterns = [
    # Auth
        path('profil-sozlamalari/', views.profil_sozlamalari, name='profil_sozlamalari'),
    path('login-ozgartirish/', views.login_ozgartirish, name='login_ozgartirish'),
    path('parol-ozgartirish/', views.parol_ozgartirish, name='parol_ozgartirish'),
    path('rasm-ochirish/', views.rasm_ochirish, name='rasm_ochirish'),
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register_view, name='register'),
    
    # Xodimlar
    path('xodimlar/', views.xodimlar, name='xodimlar'),
    path('xodim/<int:pk>/', views.xodim_detail, name='xodim_detail'),
    path('xodim-qoshish/', views.xodim_qoshish, name='xodim_qoshish'),
    path('xodim/<int:pk>/tahrirlash/', views.xodim_tahrirlash, name='xodim_tahrirlash'),
    path('xodim/<int:pk>/ochirish/', views.xodim_ochirish, name='xodim_ochirish'),
    
    # Bonus va Jarima
    path('bonus-qoshish/', views.bonus_qoshish, name='bonus_qoshish'),
    path('jarima-qoshish/', views.jarima_qoshish, name='jarima_qoshish'),
    path('bonus/<int:pk>/ochirish/', views.bonus_ochirish, name='bonus_ochirish'),
    path('jarima/<int:pk>/ochirish/', views.jarima_ochirish, name='jarima_ochirish'),
    
    # Pul yechish
    path('xodim/<int:pk>/bonus-pul-yechish/', views.bonus_pul_yechish, name='bonus_pul_yechish'),
    path('xodim/<int:pk>/jarima-pul-yechish/', views.jarima_pul_yechish, name='jarima_pul_yechish'),
    path('xodim/<int:pk>/reytingdan-yechish/', views.reytingdan_yechish, name='reytingdan_yechish'),
    
    # Reyting va Hisobot (MUHIM - CSV va PDF ni qo'shdim)
    path('reytinglar/', views.reytinglar, name='reytinglar'),
    path('oylik-hisobot/', views.oylik_hisobot, name='oylik_hisobot'),
    path('oylik-hisobot/excel/', views.oylik_hisobot_excel, name='oylik_hisobot_excel'),
    path('oylik-hisobot/csv/', views.oylik_hisobot_csv, name='oylik_hisobot_csv'),
    path('oylik-hisobot/pdf/', views.oylik_hisobot_pdf, name='oylik_hisobot_pdf'),
    path('barcha-malumotlar-excel/', views.barcha_malumotlar_excel, name='barcha_malumotlar_excel'),
    
    # Profil
    path('mening-profilim/', views.mening_profilim, name='mening_profilim'),
    path('profil-sozlamalari/', views.profil_sozlamalari, name='profil_sozlamalari'),
       path('xodim/<int:pk>/ballarni-tekislash/', views.xodim_ballarni_tekislash, name='xodim_ballarni_tekislash'),
    # Boshqaruv
    path('sabablar-boshqaruvi/', views.sabablar_boshqaruvi, name='sabablar_boshqaruvi'),
    path('tarixlar/', views.tarixlar, name='tarixlar'),
    path('xodim/<int:pk>/tarixlar/', views.tarixlar, name='xodim_tarixlar'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/', views.admin, name='admin'),
        path('xodim/<int:pk>/bonus-ball-yechish/', views.bonus_ball_yechish, name='bonus_ball_yechish'),
    path('xodim/<int:pk>/jarima-ball-yechish/', views.jarima_ball_yechish, name='jarima_ball_yechish'),

    # Shop
    path('shop/', views.shop_view, name='shop'),
    path('shop/purchase/<int:product_id>/', views.purchase_view, name='purchase_product'),
    path('my-orders/', views.my_orders_view, name='my_orders'),

    # Mahsulot boshqaruvi (admin)
    path('mahsulot-qoshish/', views.mahsulot_qoshish, name='mahsulot_qoshish'),
    path('mahsulotlar/', views.admin_mahsulotlar, name='admin_mahsulotlar'),
    path('mahsulot/<int:product_id>/tahrirlash/', views.shop_edit_view, name='mahsulot_tahrirlash'),
    path('mahsulot/<int:product_id>/ochirish/', views.mahsulot_ochirish, name='mahsulot_ochirish'),

    # Kategoriya boshqaruvi (admin)
    path('kategoriya-qoshish/', views.kategoriya_qoshish, name='kategoriya_qoshish'),
    path('kategoriya/<int:pk>/ochirish/', views.kategoriya_ochirish, name='kategoriya_ochirish'),

    # Admin orders
    path('admin/orders/', views.admin_order_list, name='admin_order_list'),
    path('admin/orders/<int:order_id>/approve/', views.admin_order_approve, name='admin_order_approve'),
    path('admin/orders/<int:order_id>/reject/', views.admin_order_reject, name='admin_order_reject'),

    # Bildirishnomalar
    path('bildirishnomalar/', views.notification_list, name='notification_list'),
    path('bildirishnomalar/ochilmagan-soni/', views.notification_unread_count, name='notification_unread_count'),
    path('bildirishnoma/<int:pk>/oqildi/', views.notification_mark_read, name='notification_mark_read'),
    path('bildirishnomalar/barchasi-oqildi/', views.notification_mark_all_read, name='notification_mark_all_read'),

    # Push bildirishnomalar (PWA)
    path('push/subscribe/', views.push_subscribe, name='push_subscribe'),
    path('push/unsubscribe/', views.push_unsubscribe, name='push_unsubscribe'),
    path('push/vapid-public-key/', views.vapid_public_key, name='vapid_public_key'),
]