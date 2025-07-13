let chartDate;
let chartInjury;
let chartDeath;

document.addEventListener('DOMContentLoaded', () => {
    new Chart(document.getElementById('chartDay'), {
        type: 'bar',
        data: {
            labels: chartLabelsDay,
            datasets: [{
                label: 'Jumlah Berita',
                data: chartDataDay,
                backgroundColor: '#fec80c'
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    new Chart(document.getElementById('chartVehicle'), {
        type: 'bar',
        data: {
            labels: chartLabelsVehicle,
            datasets: [{
                label: 'Jumlah Berita',
                data: chartDataVehicle,
                backgroundColor: '#fec80c'
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    new Chart(document.getElementById('chartMerk'), {
        type: 'bar',
        data: {
            labels: chartLabelsMerk,
            datasets: [{
                label: 'Jumlah Berita',
                data: chartDataMerk,
                backgroundColor: '#fec80c'
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    new Chart(document.getElementById('chartAge'), {
        type: 'bar',
        data: {
            labels: chartLabelsAge,
            datasets: [{
                label: 'Jumlah Korban',
                data: chartDataAge,
                backgroundColor: '#fec80c'
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    new Chart(document.getElementById('chartRoad'), {
        type: 'bar',
        data: {
            labels: chartLabelsRoad,
            datasets: [{
                label: 'Jumlah Berita',
                data: chartDataRoad,
                backgroundColor: '#fec80c'
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    new Chart(document.getElementById('chartTime'), {
        type: 'bar',
        data: {
            labels: chartLabelsTime,
            datasets: [{
                label: 'Jumlah Berita',
                data: chartDataTime,
                backgroundColor: '#fec80c'
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });

    new Chart(document.getElementById('chartCause'), {
        type: 'bar',
        data: {
            labels: chartLabelsCause,
            datasets: [{
                label: 'Jumlah Berita',
                data: chartDataCause,
                backgroundColor: '#fec80c'
            }]
        },
        options: {
            plugins: {
                legend: { display: false }
            },
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
});

const map = L.map('map').setView([-7.2, 110.5], 8); // fokus Jawa Tengah

L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

function getColor(d) {
    return d > 160 ? '#800026' :   // 161–173
        d > 140 ? '#BD0026' :   // 141–160
            d > 120 ? '#E31A1C' :   // 121–140
                d > 100 ? '#FC4E2A' :   // 101–120
                    d > 80 ? '#FD8D3C' :   // 81–100
                        d > 60 ? '#FEB24C' :   // 61–80
                            d > 40 ? '#FED976' :   // 41–60
                                d > 20 ? '#FFEDA0' :   // 21–40
                                    d > 0 ? '#FFFFCC' :   // 1–20
                                        '#eeeeee';   // 0
}


function style(feature) {
    return {
        fillColor: getColor(feature.properties.jumlah),
        weight: 1,
        opacity: 1,
        color: 'gray',
        dashArray: '3',
        fillOpacity: 0.7
    };
}

function onEachFeature(feature, layer) {
    const nama = feature.properties.WADMKK;
    const jumlah = feature.properties.jumlah;
    layer.bindPopup(`<b>${nama}</b><br>Jumlah Berita: ${jumlah}`);
}

L.geoJson(geojsonData, {
    style: style,
    onEachFeature: onEachFeature
}).addTo(map);

// === Tambahkan legenda ===
const legend = L.control({ position: 'bottomright' });

legend.onAdd = function (map) {
    const div = L.DomUtil.create('div', 'info legend');
    //const grades = [0, 1, 6, 11, 21, 51];  // nilai batas sesuai dengan getColor
    const grades = [0, 1, 21, 41, 61, 81, 101, 121, 141, 161]; // nilai batas sesuai dengan getColor
    const labels = [];

    for (let i = 0; i < grades.length; i++) {
        const from = grades[i];
        const to = grades[i + 1];

        if (from === 0 && to) {
            labels.push(
                '<i style="background:' + getColor(from) + '"></i> ' +
                '0');
        } else {
            labels.push(
                '<i style="background:' + getColor(from) + '"></i> ' +
                from + (to ? '&ndash;' + (to - 1) : '+'));
        }

    }

    div.innerHTML = '<strong>Jumlah Berita</strong><br>' + labels.join('<br>');

    return div;
};

legend.addTo(map);

// --- Logika untuk Modal Word Cloud ---
const showWordcloudButton = document.getElementById('showCauseWordcloudIcon');
const wordcloudModal = document.getElementById('wordcloudCauseModal');
const closeWordcloudButton = document.getElementById('closeWordcloudModalBtn');
const wordcloudImageElement = document.getElementById('wordcloudCauseImage');
const loadingTextElement = document.getElementById('wordcloudLoadingText');
const errorTextElement = document.getElementById('wordcloudErrorText');

if (showWordcloudButton) {
    showWordcloudButton.addEventListener('click', function () {
        wordcloudModal.style.display = 'block';
        loadingTextElement.style.display = 'block';
        wordcloudImageElement.style.display = 'none';
        errorTextElement.style.display = 'none';

        // Ambil nilai filter dari form atau URL
        // Pastikan ID elemen form filter sesuai
        // const startDate = document.getElementById('start_date') ? document.getElementById('start_date').value : '';
        // const endDate = document.getElementById('end_date') ? document.getElementById('end_date').value : '';
        // const lokasi = document.getElementById('lokasi') ? document.getElementById('lokasi').value : '';

        // Alternatif: Ambil dari URL jika filter diterapkan via GET request ke halaman ini
        const urlParams = new URLSearchParams(window.location.search);
        const startDate = urlParams.get('start_date') || '';
        const endDate = urlParams.get('end_date') || '';
        const lokasi = urlParams.get('lokasi') || '';

        let fetchUrl = `/generate_wordcloud_cause?cache_bust=${new Date().getTime()}`; // Cache busting
        if (startDate) fetchUrl += `&start_date=${encodeURIComponent(startDate)}`;
        if (endDate) fetchUrl += `&end_date=${encodeURIComponent(endDate)}`;
        if (lokasi && lokasi !== 'semua') fetchUrl += `&lokasi=${encodeURIComponent(lokasi)}`;

        fetch(fetchUrl)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(errData => { // Coba baca error dari JSON
                        throw new Error(errData.error || `Gagal mengambil data (HTTP ${response.status})`);
                    }).catch(() => { // Jika tidak ada JSON error, lempar error HTTP biasa
                        throw new Error(`Gagal mengambil data (HTTP ${response.status})`);
                    });
                }
                return response.json();
            })
            .then(data => {
                loadingTextElement.style.display = 'none';
                if (data.wordcloud_image) {
                    wordcloudImageElement.src = 'data:image/png;base64,' + data.wordcloud_image;
                    wordcloudImageElement.style.display = 'block';
                    if (data.message) { // Tampilkan pesan tambahan jika ada (mis. "Tidak ada data")
                        errorTextElement.textContent = data.message;
                        errorTextElement.style.display = 'block';
                    } else {
                        errorTextElement.style.display = 'none';
                    }
                } else if (data.error) {
                    errorTextElement.textContent = `Error: ${data.error}`;
                    errorTextElement.style.display = 'block';
                } else {
                    errorTextElement.textContent = 'Format respons tidak dikenali.';
                    errorTextElement.style.display = 'block';
                }
            })
            .catch(error => {
                loadingTextElement.style.display = 'none';
                errorTextElement.textContent = `Terjadi kesalahan: ${error.message}`;
                errorTextElement.style.display = 'block';
                console.error('Error fetching word cloud:', error);
            });
    });
}

if (closeWordcloudButton) {
    closeWordcloudButton.addEventListener('click', function () {
        wordcloudModal.style.display = 'none';
        wordcloudImageElement.src = ''; // Kosongkan src untuk membersihkan
    });
}

// Tutup modal jika klik di luar area konten modal
window.addEventListener('click', function (event) {
    if (event.target === wordcloudModal) {
        wordcloudModal.style.display = 'none';
        wordcloudImageElement.src = ''; // Kosongkan src
    }
});

// Tutup modal dengan tombol Escape
window.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && wordcloudModal.style.display === 'block') {
        wordcloudModal.style.display = 'none';
        wordcloudImageElement.src = ''; // Kosongkan src
    }
});


// ================================= CHART DATE =========================================================
function renderChartDate(labels, data) {
    if (chartDate) chartDate.destroy();
    chartDate = new Chart(document.getElementById('chartDate').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Jumlah Berita',
                data: data,
                backgroundColor: '#fec80c',
                borderColor: '#fec80c',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } }
        }
    });
}

function updateChartDate() {
    const periode = document.querySelector('input[name="periode"]:checked').value;
    const urlParams = new URLSearchParams(window.location.search);
    const startDate = urlParams.get('start_date') || '';
    const endDate = urlParams.get('end_date') || '';
    const lokasi = urlParams.get('lokasi') || '';

    let url = `/get_chart_date?periode=${periode}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    if (lokasi && lokasi !== 'semua') url += `&lokasi=${lokasi}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderChartDate(data.labels_date, data.data_date);
        });
}

document.querySelectorAll('input[name="periode"]').forEach(r => {
    r.addEventListener('change', updateChartDate);
});

document.addEventListener('DOMContentLoaded', updateChartDate);

// ================================= CHART INJURY =========================================================
function renderChartInjury(labels, data) {
    if (chartInjury) chartInjury.destroy();
    chartInjury = new Chart(document.getElementById('chartInjury').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Jumlah Korban',
                data: data,
                backgroundColor: '#fec80c',
                borderColor: '#fec80c',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } }
        }
    });
}

function updateChartInjury() {
    const periode = document.querySelector('input[name="periode_injury"]:checked').value;
    const urlParams = new URLSearchParams(window.location.search);
    const startDate = urlParams.get('start_date') || '';
    const endDate = urlParams.get('end_date') || '';
    const lokasi = urlParams.get('lokasi') || '';

    let url = `/get_chart_injury?periode_injury=${periode}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    if (lokasi && lokasi !== 'semua') url += `&lokasi=${lokasi}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderChartInjury(data.labels_injury, data.data_injury);
        });
}

document.querySelectorAll('input[name="periode_injury"]').forEach(r => {
    r.addEventListener('change', updateChartInjury);
});

document.addEventListener('DOMContentLoaded', updateChartInjury);

// ================================= CHART DEATH =========================================================
function renderChartDeath(labels, data) {
    if (chartDeath) chartDeath.destroy();
    chartDeath = new Chart(document.getElementById('chartDeath').getContext('2d'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Jumlah Korban',
                data: data,
                backgroundColor: '#fec80c',
                borderColor: '#fec80c',
                tension: 0.1,
                fill: false
            }]
        },
        options: {
            plugins: { legend: { display: false } },
            responsive: true,
            maintainAspectRatio: false,
            scales: { y: { beginAtZero: true } }
        }
    });
}

function updateChartDeath() {
    const periode = document.querySelector('input[name="periode_death"]:checked').value;
    const urlParams = new URLSearchParams(window.location.search);
    const startDate = urlParams.get('start_date') || '';
    const endDate = urlParams.get('end_date') || '';
    const lokasi = urlParams.get('lokasi') || '';

    let url = `/get_chart_death?periode_death=${periode}`;
    if (startDate) url += `&start_date=${startDate}`;
    if (endDate) url += `&end_date=${endDate}`;
    if (lokasi && lokasi !== 'semua') url += `&lokasi=${lokasi}`;

    fetch(url)
        .then(response => response.json())
        .then(data => {
            renderChartDeath(data.labels_death, data.data_death);
        });
}

document.querySelectorAll('input[name="periode_death"]').forEach(r => {
    r.addEventListener('change', updateChartDeath);
});

document.addEventListener('DOMContentLoaded', updateChartDeath);