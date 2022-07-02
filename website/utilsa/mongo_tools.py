from website import fyp_db
from Cryptodome.Cipher import AES
import argon2
import ast 
#To do list. tukar email to become ID, encrpytopm
def insert_doc_db(doc):
  collection = fyp_db.a
  return collection.insert_one(doc)

def add_entry(email, new):
  collection = fyp_db.a
  new["P_Id"] = getLastP_Id(collection, email) + 1
  return collection.update_one({'email': email}, {'$push': {'passwords': new}}, upsert = True)

def get_content_by_email(email):
  collection = fyp_db.a
  #print(type(collection.find_one({"email": email})))
  return (collection.find_one({"email": email}))

def update_entry(email, ciphertext, tag, nonce):
  collection = fyp_db.a
  #Original
  #new["P_Id"] = id
  #return (collection.find_one_and_update(
  #  {'email': email, "passwords.P_Id":  id},
  #  {'$set': {'passwords.$': new}}
  #   ))
  return (collection.find_one_and_update({'email': email},
                                         {'$set': {'tag': tag, 'nonce': nonce, 'ciphertext': ciphertext}}))

def delete_entry(email, id):
  collection = fyp_db.a
  #1. Make a delete, kita test kat akhir2
  #2. Update the ID value using the update many, $inc -1, $gte ...

  collection.find_one_and_update(
    {"email":email},
    {'$pull': {'passwords': {"P_Id": id}}
     })
  
  collection.update_many(
   {"email":email},
   {
      "$inc": {"passwords.$[elem].P_Id": -1},
   },
    array_filters = [{"elem.P_Id": {"$gte" : id}}],
    upsert=False
  )

def getLastP_Id(self,email):
  a = self.find_one({"email":email})
  if len(a["passwords"]) != 0:
    last_id = sorted(a["passwords"], key= lambda item:item['P_Id'], reverse=True)
    return int(last_id[0]["P_Id"])
  else:
    return 0
  
def enc(key, dat):
    
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest((str(dat)).encode('utf-8')) #Truns the plain text into ciphertext. Ciphertext = the password entries, tag = verification purposes
    nonce1 = cipher.nonce #Saved somewhere with the database for each entry. Need saving
    return ciphertext, tag, nonce1

def denc(key, ciphertext, tag, nonce1):
  
    cipher = AES.new(key, AES.MODE_GCM, nonce1) #Has to be done like this
    data = cipher.decrypt_and_verify(ciphertext, tag)
    
    dec_data = data.decode('UTF-8')
    #Uncomment this when dh siap bgi kan dia jadi array of dicts 
    data = ast.literal_eval(dec_data) #The decoded ciphertext in list form
    print(dec_data)
    return data
  
def key_der(password, salt):
  
  key = argon2.low_level.hash_secret_raw( #This is the key. This will not be SAVED. This is used instead as we dont want the key to be saved
    memory_cost=512,
    time_cost=2,
    parallelism=2,
    hash_len=16,
    secret = password.encode('utf-8'), #Converts the string into bytes
    salt= salt.encode('utf-8'), #Converts the string into bytes
    type= argon2.Type.ID, #Specify to use Argon2id
    )
  return key