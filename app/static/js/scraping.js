// document.getElementById("scrapButton").addEventListener("click", function () {
//     const button = this;
//     const loading = document.getElementById("loading");
//     const result = document.getElementById("result");

//     button.disabled = true;
//     loading.style.display = "block";
//     result.innerHTML = "";

//     fetch("/start-scraping", {
//         method: "POST"
//     })
//         .then(response => response.json())
//         .then(data => {
//             loading.style.display = "none";
//             button.disabled = false;
//             result.innerHTML = `<b>✅ Scraping selesai!</b><br>Jumlah artikel: ${data.jumlah}`;
//         })
//         .catch(error => {
//             loading.style.display = "none";
//             button.disabled = false;
//             result.innerHTML = `<span style="color:red">❌ Terjadi kesalahan saat scraping</span>`;
//             console.error(error);
//         });
// });

document.addEventListener('DOMContentLoaded', function () {
    const button = document.getElementById('scrapButton');
    if (button) {
        button.addEventListener('click', function () {
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').innerText = '';

            fetch('/full-pipeline', { method: 'POST' })
                .then(res => res.json())
                .then(data => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').innerText = `✅ Berhasil scraping ${data.scraped} berita.`;
                })
                .catch(err => {
                    document.getElementById('loading').style.display = 'none';
                    document.getElementById('result').innerText = '❌ Terjadi kesalahan.';
                });
        });
    } else {
        console.error('Element #scrapButton tidak ditemukan di halaman.');
    }
});

function loadScrapingResults() {
    fetch('/load-scraping-data')
        .then(res => res.json())
        .then(result => {
            const data = result.data || [];
            const lastUpdate = result.tanggal_terbaru || 'Tidak tersedia';

            // Tampilkan tanggal terbaru ke elemen HTML
            document.getElementById('last-update').textContent = lastUpdate;

            // Tampilkan data hasil scraping ke tabel
            const tbody = document.querySelector('#resultTable tbody');
            tbody.innerHTML = '';

            data.forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td> 
                    <td>${row.title}</td>
                    <td>${row.news_date}</td>
                    <td><a href="${row.link}" target="_blank">Lihat</a></td>
                    <td>${row.content.slice(0, 200)}...</td>
                    <td>${row.sentiment}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Gagal memuat data:', error);
            document.getElementById('last-update').textContent = 'Terjadi kesalahan saat memuat data.';
        });
}



// Jika ingin load data saat halaman dibuka
window.onload = loadScrapingResults;


