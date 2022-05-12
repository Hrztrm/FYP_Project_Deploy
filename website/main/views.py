from audioop import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import json
from pathlib import Path
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework import views, permissions
from rest_framework.decorators import *
from . import serializers
from rest_framework.permissions import AllowAny, IsAuthenticated

# Create your views here.
def home(response): #Response can be changed to other names, it refers a response/request from user
    return render(response, 'main/home.html')

#Testing another way of logging in
@login_required(login_url="/login")
def secret(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username,password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
    else:
        return render(request,'secret/secret.html')

@login_required(login_url="/login")
def fpass(request):
    #Add a description sekali for the apllicaiton usrename/passwords
    fname = request.user.username
    path = Path("main/Pass_Files/" + fname + ".json")
    if not path.is_file():
        with open(path, 'w') as f:
            starter = []
            json.dump(starter, f)
            print("FILE CREATED")
            return render(request, "fpass/fpass.html") #Renders a blank template
    if(request.method=="POST"): #Saves the input from the user
        desc = request.POST['Description']
        username = request.POST['username']
        password = request.POST['password']
        with open(path, 'r+') as f:
            data = json.load(f)
            if bool(data) :
                for i in data:
                    num = i["id"]
                    user_input = {"id":num+1, "Description":desc, "Name":username, "Password":password}
            else:
                user_input = {"id":1, "Description":desc, "Name":username, "Password":password}
            data.append(user_input)
            f.seek(0)
            json.dump(data,f)
        
    #list/dict masukkan dlm value. Passkan ke dlm render. Dlm html file nnt aq cycle through it and print everything
    with open(path, 'r') as f:
        data = json.load(f)
        return render(request, "fpass/fpass.html", {'Creds':data})

def update(request, id):
    path = Path("main/Pass_Files/" + request.user.username + ".json")
    with open(path, 'r') as f:
        data = json.load(f)
        det_data = data[id-1]
    return render(request, "fpass/update.html", {'Creds':det_data})

def updaterecord(request, id):
    desc = request.POST['Description']
    username = request.POST['username']
    password = request.POST['password']
    path = Path("main/Pass_Files/" + request.user.username + ".json")
    with open(path, 'r+') as f:
        data = json.load(f)
        data[id-1]["Description"] = desc
        data[id-1]["Name"] = username
        data[id-1]["Password"] = password
        f.seek(0)
        f.truncate()
        json.dump(data,f)
    return redirect('/pass')

#deletes a record in JSON file
def delete(request, id):
    path = Path("main/Pass_Files/" + request.user.username + ".json")
    with open(path, 'r+') as f:
        data = json.load(f)
        new_data = []
        for i,a in enumerate(data):
            if i != id-1:
                if i > id-1:
                    a["id"] = a["id"] - 1 #updates the id value of the file
                new_data.append(a)
        f.seek(0)
        f.truncate()
        json.dump(new_data,f)
    return redirect('/pass')

#Function based untuk dptkan info for the username and password of the user
#Look into HTTPS for Heroku for better seucirt
@api_view(['POST'])
@authentication_classes([SessionAuthentication, BasicAuthentication])
@permission_classes([AllowAny])
def login_api(request, format=None):
    serializer = serializers.LoginSerializer(data=request.data, context={'request': request })
    serializer.is_valid(raise_exception=True)
    user = serializer.validated_data['user']
    path = Path("main/Pass_Files/" + user.username + ".json")
    with open(path, 'r+') as f:
        data = json.load(f)
    return Response(data)

#Class based api, imma using funciton based for easier doing
#class LoginView(views.APIView):
#    # This view should be accessible also for unauthenticated users.
#    permission_classes = (permissions.AllowAny,)
#
#    def post(self, request, format=None):
#        serializer = serializers.LoginSerializer(data=self.request.data,
#            context={ 'request': self.request })
#        serializer.is_valid(raise_exception=True)
#        user = serializer.validated_data['user']
#        login(request, user)
#        return Response("Pawgs")