# Real-world Dushanbe 3D asset sources

## Included in the build pipeline

The build now imports a fresh OpenStreetMap extract for the area around Istiklol Monument
(roughly a 2 km district), creates building shells from mapped footprints/heights, rebuilds
road geometry from mapped centerlines, and brings in mapped plazas, greens, water and trees.
The local coordinate origin is anchored at 38.59124, 68.78162.

Source and license: OpenStreetMap contributors, © OpenStreetMap contributors, ODbL 1.0.
The fetched extract and attribution travel with the build artifact. See assets/osm/README.md.

This is a much better real-world spatial base than hand-placed rectangular masses. It is
not a photogrammetry model: where OSM has no exact height or facade tags, the importer
estimates heights and adds procedural facade windows. Surveyed facades, roof details and
photographic textures are not implied.

## Specific existing Dushanbe 3D models found

These public model pages have download controls on 3D Warehouse or link back to that source.
They are not redistributed in this repository because the search results do not expose a
clear open redistribution license. Acquire each from its source page and retain creator credit.

| Model | Source and notes |
|---|---|
| Dushanbe Flagpole — by Sebastian S. | https://embed-3dwarehouse-classic.sketchup.com/model/ed3e6a6af7bbb6b572f10cdc3d99c641/Dushanbe-Flagpole — 597 polygons, page states bounds 65 × 46 × 168 m. This is near Palace of Nations, not the new Istiklol Monument. |
| Skyscraper in Dushanbe — by Sebastian Sosnowski | https://embed-3dwarehouse-classic.sketchup.com/model/1eee42aa9948e2c7ff63cc79115e9313/Skyscraper-in-Dushanbe — 7,585 polygons per the source page. |
| Palace of Nations, Dushanbe | https://3dmdb.com/en/3d-model/palace-of-nations-dushanbe-tajikistan/6382879/ — catalog page links to its 3D Warehouse source. |
| Broad Dushanbe GIS city model | https://www.cgtrader.com/3d-models/architectural/architectural-street/dushanbe — paid Blender file, about $15 on the page reviewed; description says buildings are untextured. Not a suitable free photorealistic drop-in. |
| Dushanbe city model, 25 km | https://www.turbosquid.com/3d-models/dushanbe-city-tajikistan-model-2085991 — paid GIS-based city model, about $49 on the page reviewed. Vendor describes low-poly geometry and no elevation; other listing notes some buildings may be AI-generated. It is not a one-to-one facade reconstruction. |

## Next asset acquisition target

The highest-value missing model is the current Istiklol Independence Monument and its exact
plaza, with correct proportions, decorative surfaces and roof/tower geometry. No openly
licensed downloadable model of that exact object was found in this pass. To make that focal
landmark one-to-one, we need a reusable model from its author, a paid asset with suitable
project/mod distribution rights, or a photogrammetry/modeling pass from multi-view reference
imagery. Do not replace it with a vaguely similar monument and claim accuracy.


## Current Istiklol Monument: procedural replacement added to the project

The Blender build now hides the old 20 m cylinder-and-sphere placeholder and creates an original
reference-based model with the published overall height of 121 m and lower architectural section
of 30 m. Its geometry includes a multi-sided lower plinth, seven arch motifs, radial pavilions,
cupolas, pilasters, a blue segmented/twisted shaft, a viewing-gallery ring near the documented
94 m level, gold spiral ribs, and a multi-lobed crown.

Published dimension references:
- Tajikistan Academy of Architecture and Construction: https://www.aac.tj/project/47.html
- Khovar: https://khovar.tj/rus/2024/05/ploshhad-istiklol-etot-velichestvennyj-i-turisticheskij-obekt-goroda-dushanbe-pokoril-serdtsa-zhitelej-stolitsy/
- Government opening report: https://akn.tj/ru/2022/09/08/opening-of-the-istiqlal-square-and-the-architectural-complex-of-the-istiqlal-symbol-in-the-city-of-dushanbe/

The model is new project-authored procedural geometry; no third-party mesh or copyrighted photo
texture is bundled. It is based on published dimensions and visible reference, not a laser scan
or photogrammetry. Decorative tile motifs, exact roof/wall construction and material textures
still require closer reference work or a reusable source model for truly one-to-one accuracy.
