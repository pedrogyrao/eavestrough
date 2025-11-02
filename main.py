import sys
from geopy.geocoders import Nominatim
from src.footprint_loader import FootprintLoader
from src.plotter import plot_building

WASTE_FACTOR: float = 0.15


def main():
    if len(sys.argv) < 2:
        print("Usage: python main.py <address>")
        return

    address: str = sys.argv[1]

    geocoder: Nominatim = Nominatim(user_agent="eavestrough_estimator")
    location = geocoder.geocode(address, country_codes="ca")

    if not location:
        print("ERROR: Could not geocode address")
        return

    latitude: float = location.latitude
    longitude: float = location.longitude

    loader: FootprintLoader = FootprintLoader()
    building = loader.query_building_footprint(latitude, longitude)

    if not building:
        print("ERROR: No building found at this location")
        return

    perimeter_m: float = round(building.perimeter_m, 2)
    recommended_m: float = round(perimeter_m * (1 + WASTE_FACTOR), 2)

    print(f"\nPerimeter: {perimeter_m} m")
    print(f"Recommended: {recommended_m} m")
    plot_building(building.geometry, address, perimeter_m, recommended_m)


if __name__ == "__main__":
    main()
