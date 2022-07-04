from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.home, name='home'), #Default view when website is first opened
    path('pass/', views.fpass, name='fpass'),
    path('pass/update/<int:id>/', views.update, name='update'),
    path('updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    path('pass/delete/<int:id>/', views.delete, name='delete'),
    path('credits/', views.credit_pg, name='credits'),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
