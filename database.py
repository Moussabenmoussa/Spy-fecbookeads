import os
from pymongo import MongoClient

MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = "pseo_platform"

class Database:
    client: MongoClient = None
    db = None

    def connect(self):
        try:
            self.client = MongoClient(MONGO_URI)
            self.db = self.client[DB_NAME]
            print("✅ MongoDB Connected (pSEO System)")
        except Exception as e:
            print(f"❌ MongoDB Connection Failed: {e}")

    def get_collection(self, name):
        return self.db[name]

# Global Instance
db = Database()
