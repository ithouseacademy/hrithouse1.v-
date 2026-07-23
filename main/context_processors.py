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
