from pathlib import Path
import requests
import json


URL = (
    "https://raw.githubusercontent.com/"
    "nswamy14/geoJson/master/"
    "india.states.geo.json"
)

OUTPUT = (
    Path(__file__).resolve().parent
    / "frontend"
    / "assets"
    / "india-states.geojson"
)


OUTPUT.parent.mkdir(
    parents=True,
    exist_ok=True
)


print("Downloading India state boundaries...")


response = requests.get(
    URL,
    timeout=60
)

response.raise_for_status()


data = response.json()


# Make the property name compatible
# with CyberRadar's Leaflet code.

for feature in data.get("features", []):

    properties = feature.setdefault(
        "properties",
        {}
    )

    state_name = (
        properties.get("ST_NM")
        or properties.get("NAME_1")
        or properties.get("NAME")
        or properties.get("name")
        or properties.get("st_nm")
        or ""
    )

    properties["ST_NM"] = state_name


OUTPUT.write_text(
    json.dumps(
        data,
        ensure_ascii=False
    ),
    encoding="utf-8"
)


print()
print("===================================")
print("SUCCESS")
print("===================================")
print()
print("India map created:")
print(OUTPUT)
print()
print(
    "Features:",
    len(data.get("features", []))
)