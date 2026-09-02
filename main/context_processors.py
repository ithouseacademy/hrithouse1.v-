from main.models import Xodim


def user_rank_context(request):
    if request.user.is_authenticated:
        try:
            xodim = request.user.xodim
            rank = Xodim.objects.filter(
                active=True, is_archived=False, reyting_ball__gt=xodim.reyting_ball
            ).count() + 1
            return {
                'user_rank': rank,
                'user_reyting_ball': xodim.reyting_ball,
                'user_ism': xodim.ism,
            }
        except Exception:
            pass
    return {}


def admin_announcements_context(request):
    if request.user.is_authenticated and request.user.is_staff:
        from main.models import AdminAnnouncement, AdminAnnouncementRead
        read_ids = AdminAnnouncementRead.objects.filter(
            user_id=request.user.id
        ).values_list('announcement_id', flat=True)
        unread = AdminAnnouncement.objects.filter(is_active=True).exclude(
            id__in=read_ids
        ).order_by('-created_at')
        return {
            'admin_announcements': unread,
            'admin_announcements_bor': unread.exists(),
        }
    return {
        'admin_announcements': [],
        'admin_announcements_bor': False,
    }
