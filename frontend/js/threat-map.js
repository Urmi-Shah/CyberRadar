let map;
let stateLayer;
let stateData = {};

const API = "https://cyberradar.onrender.com";


async function loadMap() {

    const response = await fetch(
        `${API}/map/states`
    );

    const data = await response.json();

    stateData = data.states || {};

    if (!map) {

        map = L.map("indiaMap", {
            zoomControl: true
        }).setView(
            [22.5, 79],
            5
        );

        L.tileLayer(
            "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
            {
                maxZoom: 10,
                attribution: "&copy; OpenStreetMap"
            }
        ).addTo(map);
    }

    loadIndiaGeoJSON();
}


async function loadIndiaGeoJSON() {

    /*
       Keep the GeoJSON file locally:

       frontend/assets/india-states.geojson
    */

    const response = await fetch(
        "assets/india-states.geojson"
    );

    const geojson = await response.json();


    if (stateLayer) {

        stateLayer.remove();

    }


    stateLayer = L.geoJSON(
        geojson,
        {

            style: feature => {

                const state =
                    getStateName(feature);

                const stats =
                    stateData[state];

                return {

                    fillColor:
                        getRiskColor(
                            stats?.risk_score || 0
                        ),

                    weight: 1,

                    color: "#ffffff",

                    fillOpacity: .75
                };

            },


            onEachFeature:
                (feature, layer) => {

                    const state =
                        getStateName(feature);

                    layer.bindTooltip(
                        state,
                        {
                            sticky: true
                        }
                    );


                    layer.on({

                        click: () => {

                            showState(state);

                        },

                        mouseover: e => {

                            e.target.setStyle({

                                weight: 3,

                                fillOpacity: .95

                            });

                        },

                        mouseout: e => {

                            stateLayer.resetStyle(
                                e.target
                            );

                        }

                    });

                }

        }

    ).addTo(map);

}


function getStateName(feature) {

    return (
        feature.properties?.ST_NM ||
        feature.properties?.NAME_1 ||
        feature.properties?.name ||
        feature.properties?.State ||
        "Unknown"
    );

}


function getRiskColor(score) {

    if (score >= 75)
        return "#ef4444";

    if (score >= 50)
        return "#f97316";

    if (score >= 25)
        return "#eab308";

    return "#22c55e";

}


function showState(state) {

    const data =
        stateData[state];

    if (!data) {

        document.getElementById(
            "stateName"
        ).textContent = state;

        return;

    }


    document.getElementById(
        "stateName"
    ).textContent = state;


    document.getElementById(
        "incidentCount"
    ).textContent =
        Number(
            data.incidents || 0
        ).toLocaleString();


    document.getElementById(
        "criticalCount"
    ).textContent =
        Number(
            data.critical || 0
        ).toLocaleString();


    document.getElementById(
        "financialLoss"
    ).textContent =
        "₹" +
        formatIndianNumber(
            data.financial_loss || 0
        );


    document.getElementById(
        "affectedUsers"
    ).textContent =
        Number(
            data.affected_users || 0
        ).toLocaleString();


    document.getElementById(
        "topAttack"
    ).textContent =
        data.top_attack || "—";


    document.getElementById(
        "topCity"
    ).textContent =
        data.top_city || "—";


    document.getElementById(
        "topSector"
    ).textContent =
        data.top_sector || "—";


    const badge =
        document.getElementById(
            "riskBadge"
        );


    const score =
        data.risk_score || 0;


    badge.textContent =
        data.risk_level || "LOW";


    badge.style.background =
        getRiskColor(score);

}


function formatIndianNumber(value) {

    return Number(value)
        .toLocaleString(
            "en-IN",
            {
                maximumFractionDigits: 0
            }
        );

}


document.addEventListener(
    "DOMContentLoaded",
    loadMap
);