import os
import re
import time
import certifi
import osmium
from collections import defaultdict
from pymongo import MongoClient

# Environment Variables
PBF_FILE = os.getenv("PBF_FILE")
MONGODB_URI = os.getenv("MONGODB_URI")

# 1️⃣ STEP 1: Pehle Database Connection Test Karo
print("=" * 60)
print("🔌 Testing MongoDB Atlas Connection...")
print("=" * 60)

db = None
collection = None

try:
    client = MongoClient(
        MONGODB_URI,
        tlsCAFile=certifi.where(),
        tlsAllowInvalidCertificates=True,  # Bypasses SSL Handshake Issues
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000
    )
    # Ping database to confirm connection
    client.admin.command('ping')
    db = client["LeadFinder"]
    collection = db["leads"]
    print("✅ MongoDB Connection Successful! Proceeding with scan...\n")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not connect to MongoDB Atlas!")
    print(f"Detail: {e}")
    print("Please check your MONGODB_URI secret and Network Access (0.0.0.0/0).\n")
    exit(1)

TARGETS = {
    "restaurant",
    "cafe",
    "fast_food"
}

stats = defaultdict(int)

def normalize_phone(phone_str):
    if not phone_str:
        return None
    digits = re.sub(r"\D", "", phone_str)
    
    if len(digits) == 10:
        return "91" + digits
    elif len(digits) == 12 and digits.startswith("91"):
        return digits
    elif len(digits) > 7:
        return digits
    return None

class BusinessHandler(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.nodes_scanned = 0
        self.start = time.time()
        self.buffer = []
        self.seen_leads = set()  # Key: Phone + Name (Option A)
        self.estimated_total_nodes = 100_000_000 

    def node(self, n):
        self.nodes_scanned += 1

        # Live Progress Updates
        if self.nodes_scanned % 500000 == 0:
            elapsed = time.time() - self.start
            speed = self.nodes_scanned / elapsed if elapsed > 0 else 0
            remaining_nodes = max(0, self.estimated_total_nodes - self.nodes_scanned)
            eta_sec = remaining_nodes / speed if speed > 0 else 0

            print("\n" + "=" * 60)
            print(f"🚀 Nodes Scanned : {self.nodes_scanned:,}")
            print(f"🎯 Target Leads  : {stats['Target Leads']:,}")
            print(f"⚡ Speed         : {int(speed):,} nodes/sec")
            print(f"⏱ Elapsed Time  : {elapsed:.1f} sec")
            print(f"⌛ Estimated ETA : {eta_sec / 60:.1f} min")
            print("=" * 60)

        tags = n.tags
        amenity = tags.get("amenity")

        if amenity not in TARGETS:
            return

        raw_phone = tags.get("phone") or tags.get("contact:phone")
        website = tags.get("website") or tags.get("contact:website")

        # FILTER: Has Phone AND NO Website
        if raw_phone and not website:
            phone = normalize_phone(raw_phone)
            name = tags.get("name", "N/A")
            
            if not phone:
                stats["Invalid Phone Skipped"] += 1
                return

            # OPTION A: Unique Key = Phone + Name
            # Same phone number for different branches will be SAVED.
            unique_key = f"{phone}_{name.lower().strip()}"

            if unique_key in self.seen_leads:
                stats["Duplicates Skipped"] += 1
                return

            self.seen_leads.add(unique_key)
            stats["Target Leads"] += 1

            # Extract Coordinates safely
            lat, lon = None, None
            try:
                if n.location.valid():
                    lat = n.location.lat()
                    lon = n.location.lon()
            except Exception:
                pass

            lead = {
                "name": name,
                "phone": phone,
                "lat": lat,
                "lon": lon,
                "category": amenity
            }

            self.buffer.append(lead)

            # Batch Bulk Insert (1,000 items)
            if len(self.buffer) >= 1000:
                self.save_buffer()

    def save_buffer(self):
        if self.buffer and collection is not None:
            for attempt in range(3):
                try:
                    collection.insert_many(self.buffer, ordered=False)
                    break
                except Exception as e:
                    if attempt == 2:
                        print(f"⚠️ Batch insert failed after 3 attempts: {e}")
                    time.sleep(1)
            self.buffer.clear()

    def flush(self):
        self.save_buffer()


print("=" * 60)
print("🚀 LeadFinder AI - DB Scanner")
print("=" * 60)
print(f"📂 File : {PBF_FILE}")
print("🔍 Filtering Leads (Phone = YES | Website = NO)...")
print("=" * 60)

handler = BusinessHandler()
handler.apply_file(PBF_FILE, locations='sparse_mem_array')
handler.flush()

elapsed = time.time() - handler.start

print("\n" + "=" * 60)
print("✅ SCAN & SAVED TO MONGO COMPLETED")
print("=" * 60)
print(f"🎯 Total Leads Saved  : {stats['Target Leads']:,}")
print(f"⚠️ Duplicates Skipped : {stats['Duplicates Skipped']:,}")
print(f"📦 Total Nodes Scanned: {handler.nodes_scanned:,}")
print(f"⏱ Total Time Taken   : {elapsed:.2f} seconds")
print("=" * 60)
