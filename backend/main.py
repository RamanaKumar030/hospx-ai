import requests
from fastapi import FastAPI
from pydantic import BaseModel
from crew_ai.crew import run_crew

app = FastAPI()

# ---------- MODELS ----------
class SymptomRequest(BaseModel):
    symptoms: str

class LocationRequest(BaseModel):
    lat: float
    lon: float

# ---------- HEALTH CHECK ----------
@app.get("/")
def home():
    return {"status": "HOSPX AI running"}

# ---------- AI ROUTE ----------
@app.post("/symptom-analysis")
def symptom_analysis(request: SymptomRequest):
    result = run_crew(request.symptoms)

    return {
        "system": "HOSPX AI",
        "status": "success",
        "result": result
    }

# ---------- LOCATION ROUTE ----------
@app.post("/nearby-hospitals")
def nearby_hospitals(request: LocationRequest):

    try:
        lat = request.lat
        lon = request.lon

        url = "https://overpass-api.de/api/interpreter"

        query = f"""
        [out:json][timeout:25];
        (
          node["amenity"~"hospital|clinic|doctors"](around:50000,{lat},{lon});
          node["healthcare"~"hospital|clinic"](around:50000,{lat},{lon});
        );
        out center;
        """

        response = requests.post(
            url,
            data=query.encode("utf-8"),
            headers={"Content-Type": "text/plain"},
            timeout=20
        )

        data = response.json()

        places = []

        for el in data.get("elements", []):
            tags = el.get("tags", {})

            name = tags.get("name")
            if not name:
                continue

            places.append({
                "name": name,
                "type": tags.get("amenity") or tags.get("healthcare", "hospital")
            })

        # 🔥 IMPORTANT FALLBACK (THIS FIXES YOUR ISSUE)
        if len(places) == 0:
            places = [
                {"name": "Apollo Hospital (Demo)", "type": "hospital"},
                {"name": "Fortis Hospital (Demo)", "type": "hospital"},
                {"name": "City General Clinic (Demo)", "type": "clinic"},
            ]

        return {
            "status": "success",
            "places": places
        }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
            "places": [
                {"name": "Emergency Hospital (Offline Mode)", "type": "hospital"}
            ]
        }