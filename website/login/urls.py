from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.login_pg, name='login'),
    path('register/', views.register_pg, name='register'),
    path('logout/', views.logout_pg, name='logout'), 
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
