import pymongo
from config import *

fyp_db = pymongo.MongoClient(con_s).FYP

print("MongoDB connected")