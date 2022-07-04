import pymongo
import os

fyp_db = pymongo.MongoClient(os.environ.get('con_s')).FYP

print("MongoDB connected")