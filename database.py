import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "your_mongodb_uri_here")
client = MongoClient(MONGO_URI)
db = client['tiktok_ads_db']
ads_collection = db['ads']

def save_ad(ad_data):
    # منع التكرار بناءً على ID الإعلان
    ads_collection.update_one(
        {"ad_id": ad_data['ad_id']},
        {"$set": ad_data},
        upsert=True
    )

def get_all_ads():
    return list(ads_collection.find({}, {"_id": 0}))
