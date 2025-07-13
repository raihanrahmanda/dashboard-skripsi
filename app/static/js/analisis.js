function loadClassificationTable() {
    fetch('/load-classification-data')
        .then(res => res.json())
        .then(data => {
            console.log("DATA LOADED:", data); // 👈 Tambahkan ini

            const tbody = document.querySelector('#ClassificationTable tbody');
            if (!tbody) {
                console.error("Tbody tidak ditemukan!");
                return;
            }

            tbody.innerHTML = '';

            data.forEach((row, index) => {
                console.log("ROW:", row); // 👈 Tambahkan ini juga

                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td> 
                    <td>${row.DAY}</td>
                    <td>${row.TIME}</td>
                    <td>${row.VEHICLE}</td>
                    <td>${row.ROAD}</td>
                    <td>${row.CAUSE}</td>
                    <td>${row.DRIVER_AGE}</td>
                    <td>${row.DEATH}</td>
                `;
                tbody.appendChild(tr);
            });
        })
        .catch(err => {
            console.error("Gagal load Classification table:", err);
        });
}


document.addEventListener("DOMContentLoaded", function () {
    loadClassificationTable();
});

document.getElementById("btn-download-classification").addEventListener("click", function (event) {
    event.preventDefault(); // Cegah reload atau pindah halaman

    fetch('/download-classification-table')
        .then(response => {
            if (!response.ok) {
                alert("File tidak ada");
                throw new Error("File tidak ada");
            }
            return response.blob();
        })
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'dataset_klasifikasi_lengkap.csv';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
        })
        .catch(err => {
            console.error(err);
        });
});