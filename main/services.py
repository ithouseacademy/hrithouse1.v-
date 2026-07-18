from django.db import transaction
from django.db.models import Sum
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
import json
import base64

from .models import Product, ProductOrder, PointTransaction, Xodim, Notification, PushSubscription


def send_web_push(subscription, title, body, url='', icon='/static/img/logo.png'):
    """Send a web push notification to a single subscription"""
    from pywebpush import webpush, WebPushException

    try:
        payload = json.dumps({
            'title': title,
            'body': body,
            'url': url,
            'icon': icon,
        })

        webpush(
            subscription_info={
                'endpoint': subscription.endpoint,
                'keys': {
                    'p256dh': subscription.p256dh_key,
                    'auth': subscription.auth_key,
                }
            },
            data=payload,
            vapid_private_key=settings.VAPID_PRIVATE_KEY,
            vapid_claims={'sub': f'mailto:{settings.VAPID_CLAIM_EMAIL}'},
            ttl=86400,
        )
        return True
    except WebPushException as e:
        if e.response and e.response.status_code in (410, 404):
            subscription.delete()
        return False
    except Exception:
        return False


def send_web_push_to_user(user, title, body, url=''):
    """Send web push to all subscriptions of a user"""
    subs = PushSubscription.objects.filter(user=user)
    if not subs.exists():
        return

    for sub in subs:
        send_web_push(sub, title, body, url)


def send_web_push_to_admins(title, body, url=''):
    """Send web push to all admin subscriptions"""
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        send_web_push_to_user(admin, title, body, url)


def send_notification(user, title, message, url=''):
    Notification.objects.create(
        user=user,
        title=title,
        message=message,
        url=url
    )
    # Also send web push
    send_web_push_to_user(user, title, message, url)


def send_notification_to_admins(title, message, url=''):
    admins = User.objects.filter(is_staff=True)
    for admin in admins:
        send_notification(admin, title, message, url)


def get_available_shop_ball(xodim):
    pending = ProductOrder.objects.filter(
        user=xodim.user, status='PENDING'
    ).aggregate(total=Sum('points_spent'))['total'] or 0
    return xodim.reyting_ball - pending


@transaction.atomic
def purchase_product(user, product_id):
    product = Product.objects.select_for_update().get(id=product_id, is_active=True)

    if product.is_coming_soon:
        raise ValueError("Bu mahsulot hali sotuvga chiqmagan")

    if product.stock < 1:
        raise ValueError("Mahsulot omborda mavjud emas")

    xodim = Xodim.objects.select_for_update().get(user=user)

    available = get_available_shop_ball(xodim)
    if available < product.price_points:
        raise ValueError(
            f"Sizda yetarli ball mavjud emas. "
            f"Kerak: {product.price_points} ball, Sizda: {available} ball"
        )

    order = ProductOrder.objects.create(
        user=user,
        product=product,
        points_spent=product.price_points,
        status='PENDING'
    )

    PointTransaction.objects.create(
        user=user,
        amount=product.price_points,
        transaction_type='PURCHASE',
        description=f"{product.name} sotib olindi",
        order=order
    )

    product.stock -= 1
    product.save(update_fields=['stock'])

    # Notification: Adminlarga xabar
    ism = user.get_full_name() or user.username
    send_notification_to_admins(
        f"Yangi buyurtma",
        f"{ism} {product.name} mahsulotiga buyurtma berdi",
        '/admin/orders/'
    )

    return order


@transaction.atomic
def approve_order(order_id):
    order = ProductOrder.objects.select_for_update().get(id=order_id)

    if order.status != 'PENDING':
        raise ValueError("Buyurtma faqat PENDING holatida tasdiqlanishi mumkin")

    order.status = 'APPROVED'
    order.approved_at = timezone.now()
    order.save(update_fields=['status', 'approved_at'])

    # Xodimning xarid ballini va reyting ballini kamaytirish
    xodim = Xodim.objects.select_for_update().get(user=order.user)
    xodim.xarid_ball += order.points_spent
    xodim.reyting_ball = xodim.jami_bonus_ball - xodim.jami_jarima_ball
    xodim.save(update_fields=['xarid_ball', 'reyting_ball'])

    ism = order.user.get_full_name() or order.user.username
    send_notification(
        order.user,
        "Buyurtma tasdiqlandi",
        f"\"{order.product.name}\" mahsulotiga buyurtmangiz tasdiqlandi!",
        '/my-orders/'
    )

    return order


@transaction.atomic
def reject_order(order_id, reject_reason):
    order = ProductOrder.objects.select_for_update().get(id=order_id)

    if order.status != 'PENDING':
        raise ValueError("Buyurtma faqat PENDING holatida rad etilishi mumkin")

    if not reject_reason:
        raise ValueError("Rad etish sababini yozing")

    order.status = 'REJECTED'
    order.rejected_at = timezone.now()
    order.reject_reason = reject_reason
    order.save(update_fields=['status', 'rejected_at', 'reject_reason'])

    order.product.stock += 1
    order.product.save(update_fields=['stock'])

    send_notification(
        order.user,
        "Buyurtma rad etildi",
        f"\"{order.product.name}\" mahsulotiga buyurtmangiz rad etildi. Sabab: {reject_reason}",
        '/my-orders/'
    )

    return order
