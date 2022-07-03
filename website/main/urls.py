from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), #Default view when website is first opened
    path('pass/', views.fpass, name='fpass'),
    path('pass/update/<int:id>/', views.update, name='update'),
    path('updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    path('pass/delete/<int:id>/', views.delete, name='delete'),
    #path('login_api/', views.login_api, name = "Login_api"),
    path('credits/', views.credit_pg, name='credits'),
]
