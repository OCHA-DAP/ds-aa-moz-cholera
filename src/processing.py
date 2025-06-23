import geopandas as gpd
import rasterio
import numpy as np
import rasterstats as rs
from pathlib import Path
import os

# Define AA_DATA_DIR environment variable if not already set
AA_DATA_DIR = os.getenv("AA_DATA_DIR")

# Load admin boundaries (ADM2)
adm2_path = (
    Path(AA_DATA_DIR)
    / "public"
    / "raw"
    / "moz"
    / "cod_ab"
    / "moz_admbnda_adm2_ine_20190607.shp"
)
gdf_adm2 = gpd.read_file(adm2_path)

# Load WorldPop raster data (100m resolution, 2025)
worldpop_data_url = (
    Path(AA_DATA_DIR)
    / "public"
    / "raw"
    / "moz"
    / "worldpop"
    / "moz_pop_2025_CN_100m_R2024B_v1.tif"
)
with rasterio.open(worldpop_data_url) as worldpop_file:
    worldpop_data = worldpop_file.read(1)
    affine = worldpop_file.transform

# Mask out nodata values
worldpop_data_masked = np.ma.masked_equal(worldpop_data, -99999)

# Print basic stats
mean_value = np.mean(worldpop_data_masked)
min_value = np.min(worldpop_data_masked)
max_value = np.max(worldpop_data_masked)

print(f"Min value: {min_value}")
print(f"Max value: {max_value}")
print(f"Mean: {mean_value}")

# Zonal statistics: population sum per ADM2 unit
worldpop_data_agg = rs.zonal_stats(
    vectors=gdf_adm2,
    raster=worldpop_data_masked,
    stats=["sum"],
    nodata=-99999,
    affine=affine,
)

# Attach results back to GeoDataFrame
gdf_adm2["sum_population"] = [stat["sum"] for stat in worldpop_data_agg]

gdf_adm2[["ADM1_PT", "ADM2_PT", "ADM2_PCODE", "sum_population"]].to_csv((
    Path(AA_DATA_DIR)
    / "public"
    / "processed"
    / "moz"
    / "worldpop"
    / "adm2_population_totals.csv"
), index=False)