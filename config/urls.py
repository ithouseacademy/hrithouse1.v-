import os
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.http import Http404, FileResponse

handler404 = 'config.views.handler404'
handler500 = 'config.views.handler500'


def serve_media(request, path):
    file_path = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.isfile(file_path):
        raise Http404
    return FileResponse(open(file_path, 'rb'), content_type='application/octet-stream')


urlpatterns = [
    path('admin-site-panel-dashboard-panel-60d731db-admin/', admin.site.urls),
    path('', include('main.urls')),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    re_path(r'^media/(?P<path>.+)$', serve_media, name='serve_media'),
]
