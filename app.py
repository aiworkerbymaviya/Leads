import os
import re
import time
import certifi
import osmium
import phonenumbers
from phonenumbers import geocoder
from collections import defaultdict
from pymongo import MongoClient

# Environment Variables
PBF_FILE = os.getenv("PBF_FILE")
MONGODB_URI = os.getenv("MONGODB_URI")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", None)  # Optional ISO default (e.g. "US")

# 1️⃣ Database Connection Setup
print("=" * 60)
print("🔌 Testing MongoDB Atlas Connection...")
print("=" * 60)

db = None
collection = None

try:
    client = MongoClient(
        MONGODB_URI,
        tlsCAFile=certifi.where(),
        tlsAllowInvalidCertificates=True,
        serverSelectionTimeoutMS=10000,
        connectTimeoutMS=10000,
        socketTimeoutMS=20000
    )
    client.admin.command('ping')
    db = client["LeadFinder"]
    # 🎯 Separate Collection for Web Dev Leads
    collection = db["webdev_leads"]
    print("✅ MongoDB Connection Successful! Target Collection: 'webdev_leads'\n")
except Exception as e:
    print(f"❌ CRITICAL ERROR: Could not connect to MongoDB Atlas!")
    print(f"Detail: {e}\n")
    exit(1)

# 🎯 HIGH-CONVERSION TARGET CATEGORIES FOR WEB DEVELOPERS
# Businesses that need local web presence, booking systems, or portfolios
TARGETS = {
    # Professional & Real Estate Services
    ("office", "real_estate"): "Real Estate",
    ("office", "estate_agent"): "Real Estate",
    ("office", "property_management"): "Real Estate",
    ("office", "architect"): "Design & Architecture",
    ("office", "interior_design"): "Design & Architecture",
    ("office", "lawyer"): "Legal Services",
    ("office", "accountant"): "Financial Services",
    ("office", "employment_agency"): "Recruitment",
    ("office", "advertising_agency"): "Marketing",
    
    # Construction, Trades & Home Services
    ("office", "builder"): "Construction & Trades",
    ("office", "developer"): "Construction & Trades",
    ("craft", "electrician"): "Construction & Trades",
    ("craft", "plumber"): "Construction & Trades",
    ("craft", "carpenter"): "Construction & Trades",
    ("craft", "painter"): "Construction & Trades",
    ("craft", "photographer"): "Media & Photography",

    # Medical & Wellness Clinics
    ("amenity", "dentist"): "Healthcare",
    ("amenity", "clinic"): "Healthcare",
    ("amenity", "doctors"): "Healthcare",
    ("amenity", "veterinary"): "Healthcare",
    ("amenity", "pharmacy"): "Healthcare",
    ("shop", "medical_supply"): "Healthcare",

    # Hospitality, Food & Fitness
    ("amenity", "restaurant"): "Food & Hospitality",
    ("amenity", "cafe"): "Food & Hospitality",
    ("amenity", "fast_food"): "Food & Hospitality",
    ("tourism", "hotel"): "Food & Hospitality",
    ("tourism", "guest_house"): "Food & Hospitality",
    ("amenity", "gym"): "Fitness & Sports",

    # Automotive & Retail Shops
    ("shop", "car_repair"): "Automotive",
    ("shop", "car"): "Automotive",
    ("shop", "beauty"): "Personal Care & Beauty",
    ("shop", "hairdresser"): "Personal Care & Beauty",
    ("shop", "furniture"): "Retail",
    ("shop", "jewelry"): "Retail",
    ("shop", "optician"): "Retail"
}

stats = defaultdict(int)

def process_phone_and_country(raw_phone, tags):
    """
    Parses international phone numbers and extracts country ISO code.
    Falls back to OSM tags if available.
    """
    if not raw_phone:
        return None, None

    # Cleaning basic non-numeric chars except '+'
    clean_raw = re.sub(r"[^\d+]", "", raw_phone)
    
    formatted_phone = None
    country = tags.get("addr:country") or tags.get("country")

    # Attempt E.164 Global Parsing via phonenumbers
    try:
        # If string doesn't start with '+', try prepending '+'
        parse_str = clean_raw if clean_raw.startswith("+") else f"+{clean_raw}"
        parsed = phonenumbers.parse(parse_str, None)
        
        if phonenumbers.is_valid_number(parsed):
            formatted_phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
            if not country:
                country = phonenumbers.region_code_for_number(parsed)
    except Exception:
        pass

    # Fallback parsing if parsing with '+' failed
    if not formatted_phone:
        try:
            parsed = phonenumbers.parse(clean_raw, DEFAULT_COUNTRY)
            if phonenumbers.is_valid_number(parsed):
                formatted_phone = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
                if not country:
                    country = phonenumbers.region_code_for_number(parsed)
        except Exception:
            pass

    # Final fallback for raw digit strings if parsing fails but length is valid
    if not formatted_phone:
        digits = re.sub(r"\D", "", raw_phone)
        if len(digits) >= 8:
            formatted_phone = f"+{digits}"

    return formatted_phone, (country.upper() if country else "UNKNOWN")

class BusinessHandler(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.nodes_scanned = 0
        self.start = time.time()
        self.buffer = []
        self.seen_leads = set()
        self.estimated_total_nodes = 100_000_000 

    def node(self, n):
        self.nodes_scanned += 1

        if self.nodes_scanned % 500000 == 0:
            elapsed = time.time() - self.start
            speed = self.nodes_scanned / elapsed if elapsed > 0 else 0
            remaining_nodes = max(0, self.estimated_total_nodes - self.nodes_scanned)
            eta_sec = remaining_nodes / speed if speed > 0 else 0

            print("\n" + "=" * 60)
            print(f"🚀 Nodes Scanned : {self.nodes_scanned:,}")
            print(f"🎯 Web Dev Leads : {stats['Target Leads']:,}")
            print(f"⚡ Speed         : {int(speed):,} nodes/sec")
            print(f"⏱ Elapsed Time  : {elapsed:.1f} sec")
            print(f"⌛ Estimated ETA : {eta_sec / 60:.1f} min")
            print("=" * 60)

        tags = n.tags
        
        # Check if node matches target category
        matched_industry = None
        matched_category = None
        for (k, v), industry in TARGETS.items():
            if tags.get(k) == v:
                matched_category = v
                matched_industry = industry
                break

        if not matched_category:
            return

        raw_phone = tags.get("phone") or tags.get("contact:phone")
        website = tags.get("website") or tags.get("contact:website") or tags.get("url")

        # FILTER: MUST HAVE Phone AND MUST NOT HAVE Website
        if raw_phone and not website:
            phone, country = process_phone_and_country(raw_phone, tags)
            name = tags.get("name", "N/A")
            
            if not phone:
                stats["Invalid Phone Skipped"] += 1
                return

            unique_key = f"{phone}_{name.lower().strip()}"

            if unique_key in self.seen_leads:
                stats["Duplicates Skipped"] += 1
                return

            self.seen_leads.add(unique_key)
            stats["Target Leads"] += 1

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
                "category": matched_category,
                "industry": matched_industry,
                "country": country,  # ISO 2-letter Country Code (e.g. US, IN, DE)
                "source": "OpenStreetMap"
            }

            self.buffer.append(lead)

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
print("🚀 LeadFinder AI - Global Web Developer Outreach Scanner")
print("=" * 60)
print(f"📂 File : {PBF_FILE}")
print("🔍 Filtering SMB Leads (Phone = YES | Website = NO)...")
print("=" * 60)

handler = BusinessHandler()
handler.apply_file(PBF_FILE, locations='sparse_mem_array')
handler.flush()

elapsed = time.time() - handler.start

print("\n" + "=" * 60)
print("✅ GLOBAL WEB DEV LEADS SCAN & MONGO INGESTION COMPLETE")
print("=" * 60)
print(f"🎯 Total Leads Saved  : {stats['Target Leads']:,}")
print(f"⚠️ Duplicates Skipped : {stats['Duplicates Skipped']:,}")
print(f"📦 Total Nodes Scanned: {handler.nodes_scanned:,}")
print(f"⏱ Total Time Taken   : {elapsed:.2f} seconds")
print("=" * 60)
