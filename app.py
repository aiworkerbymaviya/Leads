import os
import re
import time
import osmium
from collections import defaultdict
from pymongo import MongoClient

# Environment Variables
PBF_FILE = os.getenv("PBF_FILE")
MONGODB_URI = os.getenv("MONGODB_URI")

# Setup MongoDB Connection
client = MongoClient(MONGODB_URI)
db = client["LeadFinder"]  # Database name
collection = db["leads"]   # Collection name

TARGETS = {
    "restaurant",
    "cafe",
    "fast_food"
}

stats = defaultdict(int)

# Phone Normalization Function
def normalize_phone(phone_str):
    if not phone_str:
        return None
    # Extract only digits
    digits = re.sub(r"\D", "", phone_str)
    
    # Simple Indian Number Normalization (Adjust logic if global needed)
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
        self.seen_phones = set()  # Duplicate Skip in Same Run
        
        # Rough total nodes per zone for ETA calculation (~100M average per zone)
        self.estimated_total_nodes = 100_000_000 

    def node(self, n):
        self.nodes_scanned += 1

        # Live Progress + Speed + ETA Calculation
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

        # FILTER: Website Skip & Phone Required
        if raw_phone and not website:
            phone = normalize_phone(raw_phone)
            
            # Skip invalid phone or Exact Duplicate (same run)
            if not phone or phone in self.seen_phones:
                stats["Duplicates/Invalid Skipped"] += 1
                return

            self.seen_phones.add(phone)
            stats["Target Leads"] += 1

            # Safely extract Lat/Lon
            lat = n.location.lat() if n.location.valid() else None
            lon = n.location.lon() if n.location.valid() else None

            # Schema Setup
            lead = {
                "name": tags.get("name", "N/A"),
                "phone": phone,
                "lat": lat,
                "lon": lon,
                "category": amenity
            }

            self.buffer.append(lead)

            # Batch Size 1000 Bulk Insert
            if len(self.buffer) >= 1000:
                collection.insert_many(self.buffer)
                self.buffer.clear()

    def flush(self):
        """Flush remaining buffer items into MongoDB."""
        if self.buffer:
            collection.insert_many(self.buffer)
            self.buffer.clear()


print("=" * 60)
print("🚀 LeadFinder AI - DB Scanner")
print("=" * 60)
print(f"📂 File : {PBF_FILE}")
print("🔍 Filtering Leads (Phone = YES | Website = NO)...")
print("=" * 60)

handler = BusinessHandler()
handler.apply_file(PBF_FILE, locations=True)
handler.flush()

elapsed = time.time() - handler.start

print("\n" + "=" * 60)
print("✅ SCAN & SAVED TO MONGO COMPLETED")
print("=" * 60)
print(f"🎯 Total Leads Saved  : {stats['Target Leads']:,}")
print(f"⚠️ Duplicates Skipped : {stats['Duplicates/Invalid Skipped']:,}")
print(f"📦 Total Nodes Scanned: {handler.nodes_scanned:,}")
print(f"⏱ Total Time Taken   : {elapsed:.2f} seconds")
print("=" * 60)
