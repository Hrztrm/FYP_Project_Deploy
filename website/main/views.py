from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import json
from pathlib import Path
from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.response import Response
from rest_framework.decorators import *
from . import serializers
from rest_framework.permissions import AllowAny
from utilsa.mongo_tools import *
import argon2, binascii
from Cryptodome.Cipher import AES
import secrets
import ast 

# Create your views here.
def home(response): #Response can be changed to other names, it refers a response/request from user
    
    password = "sd" #Gain from user
    #salt = "akljslksjdlkvj" #Get from mongodb prob or the sql. Make it 16 bytes
    salt = secrets.token_hex(16) #Creates a salt with size of 16 bytes. Save at sql db and have one for each user
    print(salt) 
    #Salt will be saved, but not the password
    #This will be the way to create and derive the key
    #The password and salt will be replaced accordingly.
    key = argon2.low_level.hash_secret_raw( #This is the key. This will not be SAVED. This is used instead as we dont want the key to be saved
    memory_cost=512,
    time_cost=2,
    parallelism=2,
    hash_len=16,
    secret = password.encode('utf-8'), #Converts the string into bytes
    salt= salt.encode('utf-8'), #Converts the string into bytes
    type= argon2.Type.ID, #Specify to use Argon2id
    )
    
    #print(binascii.hexlify(key))
    #hasher = argon2.PasswordHasher( #Random Salt for each time. I want the variable to be disposable, and will not be saved. This option requires me to save. And if the hash is then used as the key, it is stored in plaintext thus bad.
    #memory_cost=512,
    #time_cost=2,
    #parallelism=2,
    #hash_len=16,
    #salt_len=16,
    #type= argon2.Type.ID, #Specify to use Argon2id        
    #)
    #hash = hasher.hash(password) #I can do something like if verify is true, then decrypt using the key
    dat =[
        {"Desc":"UFuture",
         "Name":"Chocld121ate",
         "Passowrd": "A3d3d131dyam",
         "Type":"Login",
         "P_Id":1},
        {"Desc":"Bank Islam",
         "Name":"asasdasdasdasdd1",
         "Passowrd": "ffassdasfsaff",
         "Type":"Banking",
         "P_Id":2},
        {"Desc":"CHocolate Rain",
         "Name":"asasdfsdfd23fd33",
         "Passowrd": "dsd23f2f32222sd",
         "Type":"Login",
         "P_Id":3},
        ]
    print(type(dat))
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest((str(dat)).encode('utf-8')) #Truns the plain text into ciphertext. Ciphertext = the password entries, tag = verification purposes
    nonce1 = cipher.nonce #Saved somewhere with the database for each entry. Need saving
    print("Ciphertext:", binascii.hexlify(ciphertext)) #Need saving
    print("Tag:", binascii.hexlify(tag)) #Need saving
    print("nonce:", binascii.hexlify(nonce1)) #Save please
    
    #Decryption
    cipher = AES.new(key, AES.MODE_GCM, nonce1) #Has to be done like this
    data = cipher.decrypt_and_verify(ciphertext, tag)
    
    dec_data = data.decode('UTF-8')
    data = ast.literal_eval(dec_data) #The decoded ciphertext in list form
    print(type(data)) #The ciphertext
    print(data) #The ciphertext
    #print(response.session['favcolor'])
    return redirect('/login')

    #client.list_database_names()
    #try:
    #    client = MongoClient(connection_string)
    #    db = client.list_database_names() #The whole cluster, list all database names
    #    print(db)
    #    fyp_db = client.FYP #Enter the specific database
    #    collections = fyp_db.list_collection_names() #List all of the colletions
    #    print(collections)
    #except Exception as e:
    #    print(e)
    #return render(response, 'main/home.html') #Delete this after completion of everything

@login_required(login_url="/login")
def fpass(request):
    #Not used anymore, Used a single file to hold a user info
    #File method
    #Creates a user file if not exists
    #fname = request.user.username
    #path = Path("main/Pass_Files/" + fname + ".json")
    #if not path.is_file():
    #    with open(path, 'w') as f:
    #        starter = []
    #        json.dump(starter, f)
    #        print("FILE CREATED")
    #        return render(request, "fpass/fpass.html") #Renders a blank template
    
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
        
        #MongoDB method
        #add_entry(request.user.email, doc)

    #Not used anymore, Used a single file to hold a user info
    #File Method      
    #    with open(path, 'r+') as f:
    #        data = json.load(f)
    #        if bool(data) :
    #            for i in data:
    #                num = i["id"]
    #                user_input = {"id":num+1, "Description":desc, "Name":username, "Password":password, "p_type":p_type}
    #        else:
    #            user_input = {"id":1, "Description":desc, "Name":username, "Password":password, "p_type":p_type}
    #        data.append(user_input)
    #        f.seek(0)
    #        json.dump(data,f)
        
        #Session Var method
        p_ent = request.session['p_entry'] #Because request.session['p_entry'] is only a refrence to the list, as such it iwll save the doc
        p_ent.append(doc)
        request.session['p_entry'] = p_ent
    #File Method
    #with open(path, 'r') as f:
    #    data = json.load(f)
    #    return render(request, "fpass/fpass.html", {'Creds':data})
    
    #Uses MongoDB to store the information
    data = request.session['p_entry'] #Getting the entries for the specific user
    
    return render(request, "fpass/fpass.html", {'Creds':data})

@login_required(login_url="/login") 
def update(request, id): #Shows the update Page
    #File method
    #path = Path("main/Pass_Files/" + request.user.username + ".json")
    #with open(path, 'r') as f:
    #    data = json.load(f)
    #    det_data = data[id-1]
    
    #Uses MongoDB to store the information
    #data = get_content_by_email(request.user.email)["passwords"] #Getting the entries for the specific user. Look at aggregation
    #det_data = data[id-1]
    #det_data.update({"id":(id)})
    
    p_ent = request.session['p_entry']
    det_data = p_ent[id-1]
    return render(request, "fpass/update.html", {'Creds':det_data})

@login_required(login_url="/login")
def updaterecord(request, id):
    if(request.method=="POST"):
        if "back" in request.POST:
            return redirect(fpass)
        #Mongodb method
        #doc = {
        #    "Desc" : request.POST['Description'],
        #    "Username" : request.POST['username'],
        #    "Password" : request.POST['password'],
        #    "P_type": request.POST['P_type'],
        #}
        #update_entry(request.user.email, doc, id)
        
        #Unused, kept for references
        #File method
        #path = Path("main/Pass_Files/" + request.user.username + ".json")
        #with open(path, 'r+') as f:
        #    data = json.load(f)
        #    data[id-1]["Description"] = desc
        #    data[id-1]["Name"] = username
        #    data[id-1]["Password"] = password
        #    data[id-1]["p_type"] = p_type
        #    f.seek(0)
        #    f.truncate()
        #    json.dump(data,f)
        p_ent = request.session['p_entry']
        p_ent[id-1]["Desc"] = request.POST['Description']
        p_ent[id-1]["Username"] = request.POST['username']
        p_ent[id-1]["Password"] = request.POST['password']
        p_ent[id-1]["P_type"] = request.POST['P_type']
        request.session['p_entry'] = p_ent
    return redirect('/pass')

@login_required(login_url="/login")
#deletes a record in JSON file
def delete(request, id):
    #Uses MongoDB
    #delete_entry(request.user.email, id)
    
    #Uses File
    #path = Path("main/Pass_Files/" + request.user.username + ".json")
    #with open(path, 'r+') as f:
    #    data = json.load(f)
    #    new_data = []
    #    for i,a in enumerate(data):
    #        if i != id-1:
    #            if i > id-1:
    #                a["id"] = a["id"] - 1 #updates the id value of the file
    #            new_data.append(a)
    #    f.seek(0)
    #    f.truncate()
    #    json.dump(new_data,f)
    
    #Deletes based on session var
    p_ent = request.session['p_entry'] #Because request.session['p_entry'] is only a refrence to the list, as such it iwll save the doc
    p_ent.pop(id-1)
    request.session['p_entry'] = p_ent
    return redirect('/pass')

def credit_pg(request):
    return render(request, 'credit/credit.html')

#Function based untuk dptkan info for the username and password of the user
#Look into HTTPS for DIgital OCean   for better seucirt
#Tak buat lgi decrpytion for this
#@api_view(['POST'])
#@authentication_classes([SessionAuthentication, BasicAuthentication])
#@permission_classes([AllowAny])
#def login_api(request, format=None):
#    serializer = serializers.LoginSerializer(data=request.data, context={'request': request })
#    serializer.is_valid(raise_exception=True)
#    user = serializer.validated_data['user']
#    path = Path("main/Pass_Files/" + user.username + ".json")
#    with open(path, 'r+') as f:
#        data = json.load(f)
#    return Response(data)
