import osmium
import time
from collections import defaultdict

# Change according to workflow
PBF_FILE = "western-zone.osm.pbf"

TARGETS = {
    "restaurant",
    "cafe",
    "fast_food"
}

stats = defaultdict(int)


class BusinessHandler(osmium.SimpleHandler):

    def __init__(self):
        super().__init__()
        self.nodes_scanned = 0
        self.start = time.time()

    def node(self, n):

        self.nodes_scanned += 1

        # Progress every 500k nodes
        if self.nodes_scanned % 500000 == 0:
            elapsed = time.time() - self.start

            print("\n" + "=" * 60)
            print(f"🚀 Nodes Scanned : {self.nodes_scanned:,}")
            print(f"🍽 Restaurants   : {stats['Restaurants']:,}")
            print(f"📞 With Phone    : {stats['With Phone']:,}")
            print(f"🌐 With Website  : {stats['With Website']:,}")
            print(f"⏱ Time          : {elapsed:.1f} sec")
            print("=" * 60)

        tags = n.tags

        amenity = tags.get("amenity")

        if amenity not in TARGETS:
            return

        stats["Restaurants"] += 1

        phone = tags.get("phone") or tags.get("contact:phone")
        website = tags.get("website") or tags.get("contact:website")

        if phone:
            stats["With Phone"] += 1

        if website:
            stats["With Website"] += 1

        if phone and not website:
            stats["Phone + No Website"] += 1


print("=" * 60)
print("🚀 LeadFinder AI")
print("=" * 60)
print(f"📂 File : {PBF_FILE}")
print("🔍 Searching Restaurants...")
print("=" * 60)

handler = BusinessHandler()
handler.apply_file(PBF_FILE, locations=False)

elapsed = time.time() - handler.start

print("\n" + "=" * 60)
print("✅ SCAN COMPLETED")
print("=" * 60)

print(f"🍽 Restaurants        : {stats['Restaurants']:,}")
print(f"📞 With Phone         : {stats['With Phone']:,}")
print(f"🌐 With Website       : {stats['With Website']:,}")
print(f"❌ Phone + No Website : {stats['Phone + No Website']:,}")

print("-" * 60)
print(f"📦 Total Nodes Scanned : {handler.nodes_scanned:,}")
print(f"⏱ Total Time          : {elapsed:.2f} seconds")
print("=" * 60)
