from website import fyp_db
from Cryptodome.Cipher import AES
import argon2
import ast
def insert_doc_db(doc):
  collection = fyp_db.a
  return collection.insert_one(doc)

def get_content_by_email(email):
  collection = fyp_db.a
  return (collection.find_one({"email": email}))

def update_entry(email, ciphertext, tag, nonce):
  collection = fyp_db.a
  return (collection.find_one_and_update({'email': email},
                                         {'$set': {'tag': tag, 'nonce': nonce, 'ciphertext': ciphertext}}))

def enc(key, dat):
    
    cipher = AES.new(key, AES.MODE_GCM)
    ciphertext, tag = cipher.encrypt_and_digest((str(dat)).encode('utf-8'))
    nonce1 = cipher.nonce 
    return ciphertext, tag, nonce1

def denc(key, ciphertext, tag, nonce1):
  
    cipher = AES.new(key, AES.MODE_GCM, nonce1)
    data = cipher.decrypt_and_verify(ciphertext, tag)
    
    dec_data = data.decode('UTF-8')
    data = ast.literal_eval(dec_data) #The decoded ciphertext in list form
    return data
  
def key_der(password, salt):
  
  key = argon2.low_level.hash_secret_raw(
    memory_cost=512,
    time_cost=2,
    parallelism=2,
    hash_len=16,
    secret = password.encode('utf-8'), #Converts the string into bytes
    salt= salt.encode('utf-8'), #Converts the string into bytes
    type= argon2.Type.ID, #Specify to use Argon2id
    )
  return key