from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import torch

load_dotenv()

from backend.api.routes.chat import router as chat_router
from backend.api.routes.weather import router as weather_router
from backend.api.routes.destinations import router as destinations_router
from backend.api.routes.maps import router as maps_router
from backend.api.routes.recommendations import router as recommendations_router
from backend.api.routes.landmark import router as landmark_router
from backend.api.routes.transport import router as transport_router
from backend.api.routes.itinerary import router as itinerary_router
from backend.api.routes.scene import router as scene_router
from backend.api.routes.hotels import router as hotels_router
from backend.api.routes.trips import router as trips_router
from backend.api.routes.journal import router as journal_router

app = FastAPI(
    title="Dora AI — Smart Travel Planner API",
    description="Backend API for Dora AI Travel Assistant with Leaflet & OSRM Interactive Route Maps, Open-Meteo Weather, Tourism Dataset Knowledge Layer, Computer Vision Landmark Recognition, Places365 Scene Recognition, RailKit Train API, Makcorps Hotel API & xAI Grok Integration",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routes
app.include_router(chat_router, prefix="/api")
app.include_router(landmark_router, prefix="/api")
app.include_router(scene_router, prefix="/api")
app.include_router(transport_router, prefix="/api")
app.include_router(weather_router, prefix="/api")
app.include_router(destinations_router, prefix="/api")
app.include_router(maps_router, prefix="/api")
app.include_router(recommendations_router, prefix="/api")
app.include_router(itinerary_router, prefix="/api")
app.include_router(hotels_router, prefix="/api")
app.include_router(trips_router, prefix="/api")
app.include_router(journal_router, prefix="/api")

@app.get("/")
def read_root():
    mps_available = hasattr(torch.backends, "mps") and torch.backends.mps.is_available()
    return {
        "status": "healthy",
        "service": "Dora AI — Smart Travel Planner API",
        "device": "mps" if mps_available else "cpu",
        "torch_version": torch.__version__,
        "endpoints": ["/api/chat", "/api/weather", "/api/destinations/search", "/api/maps/route", "/health"],
        "attribution": "Weather data by Open-Meteo.com | Maps & Geocoding by OpenStreetMap & OSRM"
    }

@app.get("/health")
def health_check():
    return {"status": "ok"}
