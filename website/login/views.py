from django.shortcuts import render,redirect
from django.contrib.auth import login, logout, authenticate
from django.core.mail import send_mail
from .models import ExtendUser
from django.contrib.auth.password_validation import validate_password
import random
from django.contrib.auth.models import User
from django.contrib import messages
import re
from utilsa.mongo_tools import *
import secrets
import os

def login_pg(request):
    if (request.method=="POST"):
        if "Register" in request.POST:
            return redirect(register_pg)
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        data = {"username": username,"password":password}
        if user is not None:
            code = request.POST['code']
            if "R_OTP" in request.POST:
                ExtendUser.user = user
                ExtendUser.ver_code = str(random.randint(10000, 99999))
                print(ExtendUser.ver_code) #Can uncomment
                sending_mail(user.email, ExtendUser.ver_code) #Uncomment during real deal
                return render(request, 'login/login.html', {"data":data})
            elif 'Login' in request.POST:
                #Succesfful login
                if code == ExtendUser.ver_code:
                    ExtendUser.ver_code = secrets.token_hex(32)
                    
                    login(request, user)
                    
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

def register_pg(request):
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
        if User.objects.filter(username=username).exists(): #Duplicate email check
            messages.info(request, 'Username is already taken')
            return render(request, 'register/register.html', {"data":data})
        if password == password2: #Validation checks
            if email.split("@")[0] in username and len(email.split("@")[0]) > 3:
                messages.info(request, 'Username cannot contain beginning of email')
                return render(request, 'register/register.html', {"data":data})
            p_err = validation(password)
            if p_err:
                for a in p_err:
                    messages.info(request, a)
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
                insert_doc_db(doc)
                user = User.objects.create_user(username=username, password=password, email=email)
                user.save()

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
    
def sending_mail(email, ver_code):
    send_mail(
    'Verification Code', #Email Header
    str(ver_code), #The email body
    os.environ.get('E_host_user'), #Email from
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