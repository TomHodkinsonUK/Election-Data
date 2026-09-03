import json
import os
import re


# --------------------------------------------------
# SETTINGS
# --------------------------------------------------

SOURCE_FOLDER = (
    'congressional-district-boundaries/GeoJson'
)

OUTPUT_FOLDER = 'data/geography/house'

# House election -> Congress using that district geography
ELECTIONS = {
    1960: 87,
    1962: 88,
    1964: 89,
    1966: 90,
    1968: 91,
    1970: 92,
    1972: 93
}


# --------------------------------------------------
# CREATE OUTPUT FOLDER
# --------------------------------------------------

os.makedirs(
    OUTPUT_FOLDER,
    exist_ok=True
)


# --------------------------------------------------
# FIND ALL LEWIS GEOJSON FILES
# --------------------------------------------------

geojson_files = []

for filename in os.listdir(SOURCE_FOLDER):

    if filename.endswith('.geojson'):

        geojson_files.append(
            os.path.join(
                SOURCE_FOLDER,
                filename
            )
        )


print(
    f'Found {len(geojson_files)} Lewis GeoJSON files.'
)


# --------------------------------------------------
# CREATE ONE NATIONAL GEOJSON FOR EACH CONGRESS
# --------------------------------------------------

for election_year, congress in ELECTIONS.items():

    print()
    print(
        f'Creating {election_year} '
        f'({congress}th Congress)...'
    )

    features = []

    for filename in geojson_files:

        with open(
            filename,
            encoding='utf-8'
        ) as file:

            data = json.load(file)

        for feature in data.get(
            'features',
            []
        ):

            properties = feature.get(
                'properties',
                {}
            )

            start = properties.get(
                'startcong'
            )

            end = properties.get(
                'endcong'
            )

            # Keep districts active in this Congress
            if (
                start is not None
                and end is not None
                and start <= congress <= end
            ):

                features.append(feature)

    # --------------------------------------------------
    # REMOVE DUPLICATES
    # --------------------------------------------------

    unique_features = {}

    for feature in features:

        properties = feature.get(
            'properties',
            {}
        )

        district_id = properties.get(
            'id'
        )

        if district_id is None:

            district_id = (
                json.dumps(
                    feature,
                    sort_keys=True
                )
            )

        unique_features[district_id] = feature


    features = list(
        unique_features.values()
    )


    # --------------------------------------------------
    # CREATE NATIONAL GEOJSON
    # --------------------------------------------------

    output = {
        'type': 'FeatureCollection',
        'name': f'US_House_{election_year}',
        'crs': {
            'type': 'name',
            'properties': {
                'name':
                'urn:ogc:def:crs:EPSG::4269'
            }
        },
        'features': features
    }


    # --------------------------------------------------
    # SAVE
    # --------------------------------------------------

    output_file = os.path.join(
        OUTPUT_FOLDER,
        f'{election_year}.geojson'
    )

    with open(
        output_file,
        'w',
        encoding='utf-8'
    ) as file:

        json.dump(
            output,
            file
        )

    print(
        f'Saved {output_file}'
    )

    print(
        f'District features: {len(features)}'
    )
    