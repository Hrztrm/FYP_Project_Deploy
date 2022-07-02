from django.shortcuts import render,redirect
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from .models import ExtendUser
from django.contrib.auth.password_validation import validate_password
import random
from django.contrib.auth.models import User
from django.contrib import messages
import re
from config import *
from utilsa.mongo_tools import *
import secrets
import argon2

# Create your views here.
#Current User information is in the request
def login_pg(request):
    if (request.method=="POST"):
        if "Register" in request.POST:
            return redirect(register_pg)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        data = {"username": username,"password":password}
        if user is not None:
            #----------------------------- Ignore this part of the code. Unused for security reasons
            #This is working for 2fa, but feels unsafe, trying to create a better version
            #This will send users to a 2fa page, where code is sent to email. Then the user will be logged in
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
            #If I want to do this better, using the session can be easily exploited maybe. Gut feeling says so.
            #that extends from the user that will store the verification code
            code = request.POST['code']
            if "R_OTP" in request.POST:
                ExtendUser.user = user
                ExtendUser.ver_code = str(random.randint(10000, 99999))
                print(ExtendUser.ver_code) #Can uncomment
                #sending_mail(user.email, ExtendUser.ver_code) #Uncomment during real deal
                return render(request, 'login/login.html', {"data":data})
            elif 'Login' in request.POST:
                #Succesfful login
                if code == ExtendUser.ver_code:
                    ExtendUser.ver_code = secrets.token_hex(32)
                    
                    login(request, user)
                    
                    #Buat decrpytion and set the session with the plaintext
                    data = get_content_by_email(request.user.email)
                    key = key_der(password, data['salt'])
                    p_entry = denc(key, data['ciphertext'], data['tag'], data['nonce'])
                    request.session['p_entry'] = p_entry
                    request.session['key'] = password
                    return redirect('fpass')
                elif code == "":
                        messages.info(request, 'Please enter verification code')
                        return render(request, 'login/login.html', {"data":data})
                else:
                        messages.info(request, 'Code Incorrect')
                        return render(request, 'login/login.html', {"data":data})
        else:
            messages.info(request, 'Account not found')
            return render(request, 'login/login.html', {"data":data})

    return render(request, 'login/login.html') #Custom make the login and registeration

def register_pg(request): #Perlukan ui instruction cleanup. Validation for password and Username
    #if (request.method=="POST"):
    #    form = UserRegisterForm(request.POST)
    #    if form.is_valid():
    #        form.save()
    #        return redirect('login')
    #else:
    #    form = UserRegisterForm()
    #return render(request, 'register/register.html', {'form': form})
    #--------------------------------------------------------------------
    if (request.method=="POST"): #Customized Registeration Page
        if "back" in request.POST:
            return redirect(login_pg)
        username = request.POST['username']
        password = request.POST['password']
        password2 = request.POST['password2']
        email = request.POST['email']
        data = {"username": username, "email": email}
        
        if User.objects.filter(email=email).exists(): #Duplicate email check
            messages.info(request, 'Email is already taken')
            return render(request, 'register/register.html', {"data":data})
        if password == password2: #Validation checks
            if email.split("@")[0] in username and len(email.split("@")[0]) > 3:
                messages.info(request, 'Username cannot contain beginning of email')
                return render(request, 'register/register.html', {"data":data})
            p_err = validation(password)
            if p_err:
                messages.info(request, p_err)
                return render(request, 'register/register.html', {"data":data})
            #No errors
            try:
                salt = secrets.token_hex(16)
                p_input = [{"Desc": "Example",
                            "Username": "Example_Username",
                            "Password": "Example_Password",
                            "P_type": "General",
                            "P_Id": 0}]
                key = key_der(password, salt)
                c_text, tag, nonce = enc(key, p_input)
                
                doc = {
                    "email": email,
                    "salt": salt,
                    "tag": tag,
                    "nonce": nonce,
                    "ciphertext": c_text,
                }
                insert_doc_db(doc) #For MongoDB
                user = User.objects.create_user(username=username, password=password, email=email) #No problems with the registration
                user.save()

                print("Registeration Completed")
                #Registration completed
                return redirect('login')
            except:
                messages.info(request, "Session Time Out")
                return render(request, 'register/register.html', {"data":data})
        else:
            messages.info(request, 'Passwords do not match')
            return render(request, 'register/register.html', {"data":data})
    else:
        return render(request, 'register/register.html')
    

def logout_pg(request):
    if request.user.is_authenticated:
        data = get_content_by_email(request.user.email)
        key = key_der(request.session['key'], data['salt'])
        ciphertext, tag, nonce = enc(key, request.session['p_entry'])
        update_entry(request.user.email, ciphertext, tag, nonce)
        request.session.flush()
        logout(request)
    return redirect('login')

#Verify is unused as of now, because the current verification does not use this
#Ignore this part of the code. Unused for security reasons
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
    
def sending_mail(email, ver_code): #SMS style
    send_mail(
    'Verification Code', #Email Header
    str(ver_code), #The email body
    E_host_user, #Email from
    [email], #Email to the logged in user
    fail_silently=False,
    )
    return ver_code

def validation(passw):
    err = []
    err2 =[]
    err2 = validate_password(passw) #Checks for common, length, and all numerical
    if err2 is not None:
        for a in err2:
            err.append(str(a).split("'")[1])
    if not re.findall('[()[\]{}|\\`~!@#$%^&*_\-+=;:\'",<>./?]', passw): #Special character
        err.append("Password must contain at least 1 special character: " + "()[]{}|\`~!@#$%^&*_-+=;:'\",<>./?")
    if not (re.findall('[A-Z]', passw) and re.findall('[a-z]', passw)): #Uppercase n Lowercase
        err.append("Password must contains uppercase and lowercase letters, A-Z.")
    if not re.findall('[0-9]', passw): #Numerical
        err.append("Password must contain at least 1 digit, 0-9.")
    if len(passw) > 16: #Length of max password
        err.append("Password must be less than 16 characters")
    return err