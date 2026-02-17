from fastapi import FastAPI

from app.routers.auth import router as auth_router
from app.routers.incidents import router as incidents_router
from app.routers.routes import router as routes_router
from app.routers.stations import router as stations_router

app = FastAPI(title="Transport Reliability API", version="0.1.0")

app.include_router(auth_router)
app.include_router(incidents_router)
app.include_router(routes_router)
app.include_router(stations_router)


@app.get("/")
def root():
    return {"message": "Transport Reliability API is running"}