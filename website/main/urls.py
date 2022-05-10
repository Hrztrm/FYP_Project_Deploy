from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), #Default view when website is first opened
    path('secret/', views.secret, name='secret'), #The end '/' is important, because in the url the slash is often omitted but still sent
    path('pass/', views.fpass, name='fpass'),
    path('pass/update/<int:id>/', views.update, name='update'),
    path('updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    path('pass/delete/<int:id>/', views.delete, name='delete'),
    path('api/', views.api_home, name='api_home'),
]
