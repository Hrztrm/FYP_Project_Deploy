from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from rest_framework.decorators import *
from utilsa.mongo_tools import *

# Create your views here.
def home(response): #Response can be changed to other names, it refers a response/request from user
    return redirect('/login')

@login_required(login_url="/login")
def fpass(request):
    
    if(request.method=="POST"): #Adding Password entry
        desc = request.POST['Description']
        username = request.POST['username']
        password = request.POST['password']
        p_type = request.POST['p_type']
        try:
            p_id = request.session['p_entry'][-1]['P_Id'] + 1
        except:
            p_id = 1
        doc = {
            'Desc' : desc,
            'Username' : username,
            'Password' : password,
            'P_type': p_type,
            'P_Id': p_id,
        }
        
        p_ent = request.session['p_entry'] #Because request.session['p_entry'] is only a refrence to the list, as such it iwll save the doc
        p_ent.append(doc)
        request.session['p_entry'] = p_ent
    
    #Getting the entries for the specific user
    data = request.session['p_entry'] 
    
    return render(request, "fpass/fpass.html", {'Creds':data})

@login_required(login_url="/login") 
def update(request, id): #Shows the update Page
    
    p_ent = request.session['p_entry']
    det_data = p_ent[id-1]
    return render(request, "fpass/update.html", {'Creds':det_data})

@login_required(login_url="/login")
def updaterecord(request, id):
    if(request.method=="POST"):
        if "back" in request.POST:
            return redirect(fpass)
        p_ent = request.session['p_entry']
        p_ent[id-1]["Desc"] = request.POST['Description']
        p_ent[id-1]["Username"] = request.POST['username']
        p_ent[id-1]["Password"] = request.POST['password']
        p_ent[id-1]["P_type"] = request.POST['P_type']
        request.session['p_entry'] = p_ent
    return redirect('/pass')

#Deletes a record in JSON file
@login_required(login_url="/login")
def delete(request, id):
    p_ent = request.session['p_entry'] 
    p_ent.pop(id-1)
    request.session['p_entry'] = p_ent
    return redirect('/pass')

def credit_pg(request):
    return render(request, 'credit/credit.html')