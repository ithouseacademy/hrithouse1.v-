from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static

# Handlerlar (shu yerda bo'lishi kerak)
handler404 = 'config.views.handler404'
handler500 = 'config.views.handler500'

urlpatterns = [
    # Admin panel (murakkab URL)
    path('admin-site-panel-dashboard-panel-60d731db-admin/', admin.site.urls),
    
    # Asosiy app
    path('', include('main.urls')),
    
    # Login/Logout
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Media fayllar (faqat DEBUG=True da)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)