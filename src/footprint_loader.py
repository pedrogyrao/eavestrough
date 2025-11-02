from dataclasses import dataclass
from typing import Optional
import geopandas as gpd
from shapely.geometry import Point, Polygon
from shapely.geometry.polygon import Polygon as PolygonType
import requests

OVERPASS_URL = "http://overpass-api.de/api/interpreter"
OVERPASS_QUERY_TEMPLATE = """
[out:json][timeout:25];
(
  way["building"](around:{radius},{latitude},{longitude});
  relation["building"](around:{radius},{latitude},{longitude});
);
out geom;
"""
CRS_WGS84 = "EPSG:4326"
CRS_METRIC = "EPSG:3347"


@dataclass
class BuildingFootprint:
    geometry: PolygonType
    perimeter_m: float
    area_sqm: float
    source: str


class FootprintLoader:
    def __init__(self) -> None:
        pass

    def _get_building_from_osm(
        self, latitude: float, longitude: float, radius: int = 50
    ) -> Optional[gpd.GeoDataFrame]:
        overpass_query = OVERPASS_QUERY_TEMPLATE.format(
            radius=radius, latitude=latitude, longitude=longitude
        )

        try:
            response = requests.get(OVERPASS_URL, params={"data": overpass_query})
            data = response.json()
        except Exception:
            return

        buildings = []
        for element in data.get("elements", []):
            if element["type"] != "way" or "geometry" not in element:
                continue

            coords = [(node["lon"], node["lat"]) for node in element["geometry"]]
            if len(coords) < 3:
                continue

            buildings.append(
                {
                    "geometry": coords,
                    "osm_id": element["id"],
                    "tags": element.get("tags", {}),
                }
            )

        if not buildings:
            return

        gdf = gpd.GeoDataFrame(
            [
                {
                    "geometry": Polygon(b["geometry"]),
                    "osm_id": b["osm_id"],
                    "building_type": b["tags"].get("building", "yes"),
                }
                for b in buildings
            ],
            crs=CRS_WGS84,
        )
        return gdf

    def _find_closest_building(
        self,
        gdf: gpd.GeoDataFrame,
        latitude: float,
        longitude: float,
    ) -> Optional[gpd.GeoSeries]:
        point = gpd.GeoDataFrame(geometry=[Point(longitude, latitude)], crs=CRS_WGS84)
        gdf_proj = gdf.to_crs(CRS_METRIC)
        point_proj = point.to_crs(CRS_METRIC)
        distances = gdf_proj.distance(point_proj.geometry.iloc[0])
        closest_idx = distances.idxmin()
        return gdf.iloc[closest_idx]

    def query_building_footprint(
        self, latitude: float, longitude: float, radius: int = 50
    ) -> Optional[BuildingFootprint]:
        gdf = self._get_building_from_osm(latitude, longitude, radius)

        if gdf is None or len(gdf) == 0:
            return None

        building = self._find_closest_building(gdf, latitude, longitude)
        if building is None:
            return None

        building_gdf = gpd.GeoDataFrame([building], crs=CRS_WGS84).to_crs(CRS_METRIC)
        geom = building_gdf.geometry.iloc[0]

        return BuildingFootprint(
            geometry=geom,
            perimeter_m=geom.length,
            area_sqm=geom.area,
            source="OpenStreetMap",
        )
