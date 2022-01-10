let myChart;
let chartOriginalData = [];
// let socket;

function title_tooltip(tooltip_items) {
    return tooltip_items[0].raw.name;
}

function url_tooltip(tooltip_items) {
    return tooltip_items[0].raw.url;
}

function date_sort(a, b) {
    return a.date - b.date;
}

function handle_urls(urls, use_api) {
    chartOriginalData = [];
    // console.log(urls)
    urls.forEach((url, idx) => {
        // socket.emit("get_data", url);
        $.post('/get_data', { url: url, use_api: use_api }, function (item) {
            // console.log(item)
            populate_chart(item);
            if (idx == urls.length - 1) $("#search-btn").removeClass("spin");
        });
    });
}

function show_display_reset_btn() {
    $("#display-reset-btn").css("display", "inline");
}

function show_chart_data_reset_btn() {
    $("#chart-data-reset-btn").css("display", "inline");
}

function init_chart() {
    let ctx = document.getElementById('myChart').getContext('2d');
    myChart = new Chart(ctx, {
        type: 'line',
        data: {
            datasets: [{
                label: 'Price (S$)',
                data: [],
                borderColor: 'red',
                // lineTension: 0.4
            }]
        },
        options: {
            maintainAspectRatio: false,
            scales: {
                x: {
                    grid: {
                        // display: false
                    },
                    type: 'time',
                    time: {
                        tooltipFormat: 'DD MMM YYYY'
                    }
                },
                y: {
                    grid: {
                        // display: false
                    }
                }
            },
            parsing: {
                xAxisKey: "date",
                yAxisKey: "price"
            },
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'nearest',
                    intersect: false,
                    callbacks: {
                        beforeTitle: title_tooltip,
                        afterTitle: url_tooltip
                    }
                },
                zoom: {
                    pan: {
                        enabled: true,
                        onPanComplete() {
                            show_display_reset_btn();
                        }
                    },
                    zoom: {
                        onZoomComplete() {
                            show_display_reset_btn();
                        },
                        wheel: {
                            enabled: true,
                        },
                        pinch: {
                            enabled: true
                        },
                        mode: 'xy',
                    }
                }
            },
            hover: {
                mode: 'nearest',
                intersect: false
            },
            onClick(e) {
                if (myChart.data.datasets[0].data.length == 0) return;
                let altPressed = e.native.altKey;
                let activePoints = myChart.getElementsAtEventForMode(e, 'nearest', {
                    intersect: false
                }, false);
                if (altPressed) {
                    if (chartOriginalData.length == 0) chartOriginalData = myChart.data.datasets[0].data.slice();
                    let selectedElemIdx = activePoints[0].index;
                    myChart.data.datasets[0].data.splice(selectedElemIdx, 1);
                    myChart.update();
                    show_chart_data_reset_btn();
                }
                else { window.open(activePoints[0].element.$context.raw.url, "_blank"); }
            }
        }
    });
}

function populate_chart(item) {
    // console.log(item)
    if (!item) return;
    myChart.data.datasets[0].data.push({ date: moment(item.date, "YYYY/MM/DD"), price: item.price, name: item.name, url: item.url });
    myChart.data.datasets[0].data.sort(date_sort);
    myChart.update();
}

$("#search-form").submit(function (e) {
    e.preventDefault();
    $("#search-btn").addClass("spin");
    myChart.data.datasets[0].data = [];
    myChart.update();
    let form = $(this);
    let form_data = form.serializeArray();
    let query = form_data[0].value;
    let qty = form_data[1].value;
    let strict = $("#strict").is(":checked");
    let use_api = $("#use_api").is(":checked");
    // console.log(form_data);
    // console.log(strict);
    $.post('/query', { query: query, qty: qty, strict: strict }, function (urls) {
        handle_urls(urls, use_api)
    });
    // socket.emit("query", { "query": query, "qty": qty, "strict": strict });
});

$("#display-reset-btn").click(function () {
    myChart.resetZoom();
    $("#display-reset-btn").hide();
});

$("#chart-data-reset-btn").click(function () {
    myChart.data.datasets[0].data = chartOriginalData.slice();
    myChart.update();
    $("#chart-data-reset-btn").hide();
});

$(document).ready(function () {
    init_chart();

    // socket = io.connect();
    // socket.on('urls', function (urls) {
    // handle_urls(urls, socket);
    // });

    // socket.on("item", function (item) {
    // populate_chart(item.data);
    // });
});