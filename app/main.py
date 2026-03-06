from fastapi import FastAPI

# Import routers that define grouped API endpoints
from app.routers.auth import router as auth_router
from app.routers.incidents import router as incidents_router
from app.routers.routes import router as routes_router
from app.routers.stations import router as stations_router
from app.routers.analytics import router as analytics_router


# Main FastAPI application instance
app = FastAPI(
    title="Transport Reliability API",
    version="0.1.0"
)


# Register routers so their endpoints become part of the API
# Each router defines its own prefix (e.g. /routes, /incidents)
app.include_router(auth_router)
app.include_router(incidents_router)
app.include_router(routes_router)
app.include_router(stations_router)
app.include_router(analytics_router)


# Simple health-check / root endpoint to confirm the API is running
@app.get("/", tags=["root"])
def root():
    return {"message": "Transport Reliability API is running"}