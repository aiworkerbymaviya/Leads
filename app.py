import osmium

PBF_FILE = "western-zone.osm.pbf"


class BusinessHandler(osmium.SimpleHandler):
    def __init__(self):
        super().__init__()
        self.count = 0

    def node(self, n):
        tags = n.tags

        if "amenity" not in tags:
            return

        amenity = tags["amenity"]

        if amenity not in [
            "restaurant",
            "cafe",
            "fast_food",
            "hotel",
            "clinic",
            "hospital",
            "pharmacy",
            "bank",
            "school"
        ]:
            return

        self.count += 1

        print("=" * 50)
        print("Business :", tags.get("name", "N/A"))
        print("Category :", amenity)
        print("Phone    :", tags.get("phone", "N/A"))
        print("Website  :", tags.get("website", "N/A"))
        print("City     :", tags.get("addr:city", "N/A"))
        print("Lat      :", n.location.lat)
        print("Lon      :", n.location.lon)

        if self.count >= 10:
            raise SystemExit


handler = BusinessHandler()
handler.apply_file(PBF_FILE, locations=True)
