import osmium
from collections import defaultdict

PBF_FILE = "india.osm.pbf"

TARGETS = {
    "restaurant",
    "fast_food",
    "cafe"
}

stats = defaultdict(int)


class BusinessHandler(osmium.SimpleHandler):

    def node(self, n):

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


print("Scanning India OSM...")

handler = BusinessHandler()
handler.apply_file(PBF_FILE, locations=False)

print("\n========== RESULT ==========\n")

print(f"Restaurants          : {stats['Restaurants']:,}")
print(f"With Phone           : {stats['With Phone']:,}")
print(f"With Website         : {stats['With Website']:,}")
print(f"Phone + No Website   : {stats['Phone + No Website']:,}")

print("\n============================")
