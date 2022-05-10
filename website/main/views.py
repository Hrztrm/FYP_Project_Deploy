from audioop import reverse
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
import json
from pathlib import Path

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
    fname = request.user.username
    path = Path("main/Pass_Files/" + fname + ".json")
    if not path.is_file():
        with open(path, 'w') as f:
            starter = []
            json.dump(starter, f)
            print("FILE CREATED")
            return render(request, "fpass/fpass.html") #Renders a blank template
    if(request.method=="POST"): #Saves the input from the user
        username = request.POST['username']
        password = request.POST['password']
        with open(path, 'r+') as f:
            data = json.load(f)
            if bool(data) :
                for i in data:
                    num = i["id"]
                    user_input = {"id":num+1,"Name":username,"Password":password}
            else:
                user_input = {"id":1,"Name":username,"Password":password}
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
    username = request.POST['username']
    password = request.POST['password']
    path = Path("main/Pass_Files/" + request.user.username + ".json")
    with open(path, 'r+') as f:
        data = json.load(f)
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

def api_home(request):
    path = Path("main/Pass_Files/" + "Ikmal" + ".json")
    with open(path, 'r+') as f:
        data = json.load(f)
    
    print("Data has been sent to user")
    return JsonResponse(data)