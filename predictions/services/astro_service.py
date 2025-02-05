import math
from datetime import datetime, timezone
from typing import Any, Dict

from skyfield.api import Loader, Topos
from django.conf import settings
from django.utils import timezone as django_tz

# Helper constants/zodiac, approach adapted from the existing django logic

ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def get_zodiac_sign(ecliptic_longitude_degrees: float) -> str:
    index = int(ecliptic_longitude_degrees // 30) % 12
    return ZODIAC_SIGNS[index]


def approximate_placidus_houses(skyfield_time, latitude: float, longitude: float) -> Dict[str, float]:
    """
    Example approximation of Placidus houses.
    This is not a precise, production-grade approach, but suitable for demonstration.
    """
    # Greenwich Apparent Sidereal Time in hours
    gast = skyfield_time.gast
    lst_hours = gast + (longitude / 15.0)
    lst_hours %= 24.0

    lst_radians = math.radians((lst_hours / 24.0) * 360.0)
    lat_radians = math.radians(latitude)
    eps = math.radians(23.4392911)  # Obliquity of the ecliptic

    # Ascendant
    numerator = (math.cos(eps) * math.sin(lst_radians)) - (math.tan(lat_radians) * math.sin(eps))
    denominator = math.cos(lst_radians)
    asc_radians = math.atan2(numerator, denominator)
    asc_degrees = math.degrees(asc_radians) % 360.0

    # Midheaven
    mc_radians = math.atan2(math.tan(lst_radians), math.cos(eps))
    mc_degrees = math.degrees(mc_radians) % 360.0

    # Approximate other houses
    house_cusps = {}
    house_cusps["1"] = asc_degrees
    house_cusps["10"] = mc_degrees

    house_cusps["2"] = (asc_degrees + 30.0) % 360.0
    house_cusps["3"] = (asc_degrees + 60.0) % 360.0
    house_cusps["11"] = (mc_degrees + 60.0) % 360.0
    house_cusps["12"] = (mc_degrees + 30.0) % 360.0

    house_cusps["4"] = (house_cusps["10"] + 180.0) % 360.0
    house_cusps["5"] = (house_cusps["11"] + 180.0) % 360.0
    house_cusps["6"] = (house_cusps["12"] + 180.0) % 360.0
    house_cusps["7"] = (house_cusps["1"] + 180.0) % 360.0
    house_cusps["8"] = (house_cusps["2"] + 180.0) % 360.0
    house_cusps["9"] = (house_cusps["3"] + 180.0) % 360.0

    return house_cusps


def get_ecliptic_longitude_degrees(skyfield_pos):
    lat, lon, dist = skyfield_pos.ecliptic_latlon()
    return lon.degrees


class AstroService:
    """
    Service to handle astrological calculations using Skyfield,
    combining logic from 'vedic-ai' for demonstration.
    """

    def calculate_birth_chart(self, date_of_birth: datetime, time_of_birth: datetime, place_of_birth: str) -> Dict[str, Any]:
        """
        Combine date + time + location to produce a simplified birth chart.
        place_of_birth can be a plain string, but the logic for geocoding is not included here.
        For real usage, store lat/long in user profile and pass them in directly.
        """

        # Suppose date_of_birth is date-only, time_of_birth is a separate time object
        # Combine into single UTC-based datetime
        full_dt = datetime(
            date_of_birth.year, date_of_birth.month, date_of_birth.day,
            time_of_birth.hour, time_of_birth.minute, time_of_birth.second,
            tzinfo=timezone.utc
        )

        # For demonstration, fallback lat/lon (Paris) if none provided
        # Real code would do real geocoding or use stored lat/lon
        lat, lon = 48.8566, 2.3522
        # parse place_of_birth if "lat, lon" format:
        try:
            lat_str, lon_str = place_of_birth.split(",")
            lat = float(lat_str.strip())
            lon = float(lon_str.strip())
        except Exception:
            pass

        load = Loader("./skyfield_data")
        ts = load.timescale()
        eph = load("de421.bsp")

        t = ts.from_datetime(full_dt)

        earth = eph["earth"]
        loc = earth + Topos(latitude_degrees=lat, longitude_degrees=lon)
        loc_at_t = loc.at(t)

        # Calculate major bodies
        planet_refs = {
            "Sun": eph["sun"],
            "Moon": eph["moon"],
            "Mercury": eph["mercury"],
            "Venus": eph["venus"],
            "Mars": eph["mars"],
            "Jupiter": eph["jupiter barycenter"],
            "Saturn": eph["saturn barycenter"],
            "Uranus": eph["uranus barycenter"],
            "Neptune": eph["neptune barycenter"],
            "Pluto": eph["pluto barycenter"],
        }

        planets = {}
        for name, body in planet_refs.items():
            app = loc_at_t.observe(body).apparent()
            lon_deg = get_ecliptic_longitude_degrees(app)
            zodiac_sign = get_zodiac_sign(lon_deg)
            planets[name] = {
                "longitude_deg": round(lon_deg, 2),
                "sign": zodiac_sign,
            }

        # Approx houses
        house_cusps = approximate_placidus_houses(t, lat, lon)
        houses = {}
        for hnum in range(1, 13):
            deg = house_cusps[str(hnum)]
            houses[str(hnum)] = {
                "degree": round(deg, 2),
                "sign": get_zodiac_sign(deg),
            }

        asc_deg = houses["1"]["degree"]
        asc_sign = houses["1"]["sign"]

        birth_chart = {
            "ascendant": {"degree": asc_deg, "sign": asc_sign},
            "planets": planets,
            "houses": houses,
        }
        return birth_chart
