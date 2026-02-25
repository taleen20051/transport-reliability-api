from app.db.base_class import Base

# Import models so they are registered on Base.metadata
from app.models.route import Route  # noqa: F401
from app.models.station import Station  # noqa: F401
from app.models.user import User  # noqa: F401
from app.models.user_incident import UserIncident  # noqa: F401
from app.models.route_station import RouteStation  # noqa: F401