from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'), #Default view when website is first opened
    path('secret/', views.secret, name='secret'), #The end '/' is important, because in the url the slash is often omitted but still sent
    path('pass/', views.fpass, name='fpass'),
    path('pass/update/<int:id>/', views.update, name='update'),
    path('updaterecord/<int:id>', views.updaterecord, name='updaterecord'),
    path('pass/delete/<int:id>/', views.delete, name='delete'),
    #path('login1/', views.LoginView.as_view()), #Class based version
    path('login_api/', views.login_api, name = "Login_api"),
]
