import matplotlib.pyplot as plt
import geopandas as gpd
from matplotlib.patches import Patch
from matplotlib.figure import Figure
from shapely.geometry.polygon import Polygon

CRS_WGS84 = "EPSG:4326"
CRS_METRIC = "EPSG:3347"


def plot_building(
    geometry: Polygon, address: str, perimeter_m: float, recommended_m: float
) -> Figure:
    gdf = gpd.GeoDataFrame([{"geometry": geometry}], crs=CRS_METRIC)
    gdf_wgs84 = gdf.to_crs(CRS_WGS84)

    fig, ax = plt.subplots(figsize=(10, 10))

    gdf_wgs84.boundary.plot(ax=ax, color="red", linewidth=3)
    gdf_wgs84.plot(ax=ax, color="lightblue", alpha=0.5, edgecolor="red", linewidth=3)

    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(
        f"Building Footprint\n{address}\nPerimeter: {perimeter_m} m | Recommended: {recommended_m} m"
    )
    ax.grid(True, alpha=0.3)

    legend_elements = [
        Patch(
            facecolor="lightblue",
            alpha=0.5,
            edgecolor="red",
            linewidth=2,
            label="Building",
        ),
        Patch(
            facecolor="none",
            edgecolor="red",
            linewidth=3,
            label=f"Perimeter ({perimeter_m} m)",
        ),
    ]
    ax.legend(handles=legend_elements, loc="upper right")

    plt.tight_layout()
    plt.show()
    return fig
