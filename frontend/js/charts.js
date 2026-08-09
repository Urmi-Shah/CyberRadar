const API = "http://127.0.0.1:8000/analytics/charts";

async function loadCharts() {

    const response = await fetch(API);
    const data = await response.json();

    const ctx = document.getElementById("monthlyChart");

    new Chart(ctx, {

        type: "line",

        data: {

            labels: data.monthly.labels,

            datasets: [{

                label: "Cyber Incidents",

                data: data.monthly.values,

                borderColor: "#3b82f6",

                backgroundColor: "rgba(59,130,246,0.15)",

                borderWidth: 3,

                fill: true,

                tension: 0.4

            }]

        },

        options: {

            responsive: true,

            maintainAspectRatio: false,

            plugins: {

                legend: {

                    labels: {

                        color: "#ffffff"

                    }

                }

            },

            scales: {

                x: {

                    ticks: {

                        color: "#ffffff"

                    }

                },

                y: {

                    ticks: {

                        color: "#ffffff"

                    }

                }

            }

        }

    });

}

loadCharts();