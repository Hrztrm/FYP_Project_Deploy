from audioop import reverse
from django.shortcuts import render,redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import login, logout, authenticate
from .forms import UserRegisterForm
from django.core.mail import send_mail
from .models import ExtendUser
import random
from urllib.parse import urlencode
from django.urls import reverse

# Create your views here.
#Current User information is in the request
def login_pg(request):
    if (request.method=="POST"):
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            #-----------------------------
            #This is working for 2fa, but feels unsafe, trying to create a better version
            #send user to 2fa page, where code is sent to email. Then the user will be logged in
            #username = form.cleaned_data.get('username')
            #password = form.cleaned_data.get('password')
            #base_url = reverse('verify')
            #test = {'username' : username, 'password' : password}
            #query_string = urlencode(test) #This is VERY UNSAFE, cari cara untuk encrypt kat sikit so at least dia bukan dlm plain
            #url = '{}?{}'.format(base_url, query_string)
            #ver_code = sending_mail(user.email)
            #request.session['resp'] = ver_code
            #return redirect(url)
            #-----------------------------------
            #If I want to do this better, using the session can be easily exploited, thus i would need to create a model 
            #that extends from the user that will store the verification code
            code = request.POST['code']
            if "R_OTP" in request.POST:
                ExtendUser.user = user
                ExtendUser.ver_code = str(random.randint(1000, 9999))
                print(ExtendUser.ver_code) #Ganti dengan send_mail
                #send_mail(user.email)
                return render(request, 'login/login.html', {'form': form})
            elif 'Login' in request.POST:
                print(ExtendUser.ver_code) 
                if code == ExtendUser.ver_code:
                    print(ExtendUser.ver_code)
                    random_string = ''
                    for _ in range(30): #Resets the ver_code
                        # Considering only upper and lowercase letters
                        random_integer = random.randint(97, 97 + 26 - 1)
                        flip_bit = random.randint(0, 1)
                        # Convert to lowercase if the flip bit is on
                        random_integer = random_integer - 32 if flip_bit == 1 else random_integer
                        # Keep appending random characters using chr(x)
                        random_string += (chr(random_integer))
                    ExtendUser.ver_code = random_string
                    login(request, user)
                    return redirect('home') #Redirect to page to verifiying page
    else:
        form = AuthenticationForm()
    return render(request, 'login/login.html', {'form': form})

def register_pg(request):
    if (request.method=="POST"):
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'register/register.html', {'form': form})

def logout_pg(request):
    if request.user.is_authenticated:
        logout(request)
        return redirect('home')

#Verify is unused as of now, because the way verification is done does not use this
def verify_pg(request): #The command login is done here. The user model and authentication value is received from the login_pg.
    username = request.GET.get('username')
    password = request.GET.get('password')
    user = authenticate(username=username,password=password)
    ver_code = sending_mail(user.email)
    if (request.method=="POST"):
        Code = request.POST['code']
        print(Code)
        ver_code = request.session.get('resp')
        print(ver_code)
        if Code == str(ver_code):
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'verify/verify.html')
    else:
        return render(request, 'verify/verify.html')
    
def sending_mail(email):
    ver_code = random.randint(1000, 9999)
    send_mail(
    'Verification Code', #Email Header
    str(ver_code), #The email body
    'leeneil562@yahoo.com', #Email from
    [email], #Email to the logged in user
    fail_silently=False,
    )
    return ver_code