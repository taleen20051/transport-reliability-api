from app.db.base_class import Base

# Import models so they are registered on Base.metadata
from app.models.route import Route
from app.models.station import Station
from app.models.user import User
from app.models.user_incident import UserIncident
from app.models.route_station import RouteStation