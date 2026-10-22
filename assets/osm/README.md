# Dushanbe OpenStreetMap city-slice data

The CI workflow fetches a small Overpass API extract around the Istiklol Monument to create
a geographically aligned city model. The raw response is stored with the build artifacts
under artifacts/osm/istiklol_slice.json, not checked into Git as a frequently changing dump.

- Data source: https://www.openstreetmap.org/copyright
- Attribution: © OpenStreetMap contributors
- Database license: Open Database License (ODbL) 1.0
- Local anchor: latitude 38.59124, longitude 68.78162
- Extract bounds: 38.58200, 68.77100 to 38.60050, 68.79250

The OSM model uses footprint outlines, heights/floor counts where mapped, road centerlines,
mapped public-space polygons, and tagged trees. Where data is absent, heights and facade
windows are estimated procedurally. This is not an imagery/photogrammetry scan, and the
procedural parts do not claim to depict exact facade details.

Derived database/model data must retain applicable ODbL attribution and share-alike obligations.
Do not bundle proprietary GTA V assets or third-party 3D Warehouse files into this data folder
unless their author/license explicitly allows redistribution.
