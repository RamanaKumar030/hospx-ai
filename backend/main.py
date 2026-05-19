import uvicorn
import requests

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from crew_ai.crew import run_crew


app = FastAPI(
    title="HOSPX AI",
    description="Emergency Medical Intelligence System",
    version="1.0.0"
)

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- MODELS ----------
class SymptomRequest(BaseModel):
    symptoms: str


class LocationRequest(BaseModel):
    lat: float
    lon: float


# ---------- HEALTH CHECK ----------
@app.get("/")
def home():
    return {
        "system": "HOSPX AI",
        "status": "running",
        "message": "Backend is live"
    }


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

    lat = request.lat
    lon = request.lon

    query = f"""
    [out:json][timeout:25];
    (
      node["amenity"~"hospital|clinic|pharmacy|doctors"](around:50000,{lat},{lon});
      way["amenity"~"hospital|clinic|pharmacy|doctors"](around:50000,{lat},{lon});
      relation["amenity"~"hospital|clinic|pharmacy|doctors"](around:50000,{lat},{lon});

      node["healthcare"~"hospital|clinic|doctor|pharmacy"](around:50000,{lat},{lon});
      way["healthcare"~"hospital|clinic|doctor|pharmacy"](around:50000,{lat},{lon});
      relation["healthcare"~"hospital|clinic|doctor|pharmacy"](around:50000,{lat},{lon});
    );
    out center;
    """

    overpass_servers = [
        "https://overpass.kumi.systems/api/interpreter",
        "https://overpass-api.de/api/interpreter",
        "https://overpass.openstreetmap.ru/api/interpreter"
    ]

    last_error = ""

    for url in overpass_servers:
        try:
            response = requests.post(
                url,
                data={"data": query},
                headers={
                    "User-Agent": "HOSPX-AI/1.0",
                    "Accept": "application/json"
                },
                timeout=30
            )

            text = response.text.strip()

            if response.status_code != 200:
                last_error = f"{url} returned HTTP {response.status_code}"
                continue

            if not text.startswith("{"):
                last_error = f"{url} returned non-json: {text[:120]}"
                continue

            data = response.json()

            places = []

            for el in data.get("elements", []):
                tags = el.get("tags", {})
                name = tags.get("name")

                if not name:
                    continue

                center = el.get("center", {})

                places.append({
                    "name": name,
                    "type": tags.get("amenity") or tags.get("healthcare") or "medical",
                    "lat": el.get("lat") or center.get("lat"),
                    "lon": el.get("lon") or center.get("lon"),
                })

            if places:
                return {
                    "status": "success",
                    "source": url,
                    "places": places[:10]
                }

            last_error = f"{url} returned zero places"

        except Exception as e:
            last_error = str(e)

    return {
        "status": "fallback",
        "message": last_error,
        "places": [
            {"name": "Apollo Hospital (Demo)", "type": "hospital"},
            {"name": "Fortis Hospital (Demo)", "type": "hospital"},
            {"name": "City General Clinic (Demo)", "type": "clinic"},
        ]
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000)