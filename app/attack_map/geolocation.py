import os
import geoip2.database

DATABASE = os.path.join("geoip", "GeoLite2-City.mmdb")

reader = None

def init_geoip():
    global reader
    if not os.path.exists(DATABASE):
        print("[GeoIP] Database not found.")
        reader = None
        return
    reader = geoip2.database.Reader(DATABASE)


def locate_ip(ip_address):
    if reader is None:
        return {"error": "GeoIP not initialized"}

    try:
        response = reader.city(ip_address)

        return {
            "ip": ip_address,
            "country": response.country.name,
            "city": response.city.name,
            "latitude": response.location.latitude,
            "longitude": response.location.longitude
        }

    except Exception as e:
        return {"error": str(e)}