import requests

def get_nearby_hospitals(lat: float, lon: float, radius: int = 5000):
    """
    Fetch nearby hospitals using OpenStreetMap Overpass API (FREE)
    radius = meters (5000 = 5km)
    """

    query = f"""
    [out:json];
    (
      node["amenity"="hospital"](around:{radius},{lat},{lon});
      way["amenity"="hospital"](around:{radius},{lat},{lon});
      relation["amenity"="hospital"](around:{radius},{lat},{lon});
    );
    out center;
    """

    url = "https://overpass-api.de/api/interpreter"
    response = requests.post(url, data={"data": query})

    data = response.json()

    hospitals = []

    for element in data.get("elements", []):
        tags = element.get("tags", {})
        hospitals.append({
            "name": tags.get("name", "Unknown Hospital"),
            "lat": element.get("lat") or element.get("center", {}).get("lat"),
            "lon": element.get("lon") or element.get("center", {}).get("lon"),
        })

    return hospitals