from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_pg, name='login'), #Default view when website is first opened with /login
    path('register/', views.register_pg, name='register'), #The end '/' is important, because in the url the slash is often omitted but still sent
    path('logout/', views.logout_pg, name='logout'), #The end '/' is important, because in the url the slash is often omitted but still sent
    
]
