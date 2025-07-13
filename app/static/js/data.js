// function loadNewsTable() {
//     fetch('/load-combine-news')
//         .then(res => res.json())
//         .then(data => {
//             const tbody = document.querySelector('#NewsTable tbody');
//             tbody.innerHTML = '';

//             data.forEach((row, index) => {
//                 const tr = document.createElement('tr');
//                 tr.innerHTML = `
//                     <td>${index + 1}</td> 
//                     <td>${row.news_id || ''}</td>
//                     <td>${row.news_date || ''}</td>
//                     <td><a href="${row.link || '#'}" target="_blank">Lihat</a></td>
//                     <td>${row.title || ''}</td>
//                     <td>${(row.content || '').slice(0, 200)}...</td>

//                 `;
//                 tbody.appendChild(tr);
//             });

//             const table = $('#NewsTable').DataTable({
//                 destroy: true,
//                 scrollX: false,
//                 paging: true,
//                 searching: true,
//             });

//             // Hapus search lama dan ganti dengan filter strict match
//             $.fn.dataTable.ext.search = []; // hapus filter custom sebelumnya
//             $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
//                 const keyword = $('#NewsTable_filter input').val().trim().toLowerCase();
//                 if (!keyword) return true;

//                 for (let i = 0; i < data.length; i++) {
//                     if (data[i].toLowerCase() === keyword) {
//                         return true;
//                     }
//                 }
//                 return false;
//             });

//             // Pasang event agar search strict aktif saat user ketik
//             $('#NewsTable_filter input').off().on('input', function () {
//                 table.draw(); // trigger ulang filter strict
//             });
//         })
//         .catch(err => {
//             console.error("Gagal load news table:", err);
//         });
// }


// // function loadExtractionTable() {
// //     fetch('/load-extraction-news')
// //         .then(res => res.json())
// //         .then(data => {
// //             console.log("DATA LOADED:", data); // 👈 Tambahkan ini

// //             const tbody = document.querySelector('#ExtractionTable tbody');
// //             if (!tbody) {
// //                 console.error("Tbody tidak ditemukan!");
// //                 return;
// //             }

// //             tbody.innerHTML = '';

// //             data.forEach((row, index) => {
// //                 console.log("ROW:", row); // 👈 Tambahkan ini juga

// //                 const tr = document.createElement('tr');
// //                 tr.innerHTML = `
// //                     <td>${index + 1}</td> 
// //                     <td>${row.news_id}</td>
// //                     <td>${row.LOC}</td>
// //                     <td>${row.DAY}</td>
// //                     <td>${row.DATE}</td>
// //                     <td>${row.TIME}</td>
// //                     <td>${row.VEHICLE}</td>
// //                     <td>${row.MERK}</td>
// //                     <td>${row.ROAD}</td>
// //                     <td>${row.CAUSE}</td>
// //                     <td>${row.ORG}</td>
// //                     <td>${row.DRIVER_AGE}</td>
// //                     <td>${row.VICTIM_AGE}</td>
// //                     <td>${row.INJURY}</td>
// //                     <td>${row.DEATH}</td>
// //                 `;
// //                 tbody.appendChild(tr);
// //             });
// //         })
// //         .catch(err => {
// //             console.error("Gagal load extraction table:", err);
// //         });
// // }

// function loadExtractionTable() {
//     fetch('/load-extraction-news')
//         .then(res => res.json())
//         .then(data => {
//             console.log("DATA LOADED:", data);

//             const tbody = document.querySelector('#ExtractionTable tbody');
//             if (!tbody) {
//                 console.error("Tbody tidak ditemukan!");
//                 return;
//             }

//             tbody.innerHTML = '';

//             data.forEach((row, index) => {
//                 const tr = document.createElement('tr');
//                 tr.innerHTML = `
//                     <td>${index + 1}</td> 
//                     <td>${row.news_id || ''}</td>
//                     <td>${row.LOC || ''}</td>
//                     <td>${row.DAY || ''}</td>
//                     <td>${row.DATE_STANDARDIZED || ''}</td>
//                     <td>${row.TIME || ''}</td>
//                     <td>${row.VEHICLE || ''}</td>
//                     <td>${row.MERK || ''}</td>
//                     <td>${row.ROAD || ''}</td>
//                     <td>${row.CAUSE || ''}</td>
//                     <td>${row.ORG || ''}</td>
//                     <td>${row.DRIVER_AGE || ''}</td>
//                     <td>${row.VICTIM_AGE || ''}</td>
//                     <td>${row.INJURY || ''}</td>
//                     <td>${row.DEATH || ''}</td>
//                 `;
//                 tbody.appendChild(tr);
//             });

//             // Inisialisasi DataTable
//             const table = $('#ExtractionTable').DataTable({
//                 destroy: true,
//                 scrollX: false,
//                 paging: true,
//                 searching: true,
//             });

//             // Hapus search lama dan ganti dengan filter strict match
//             $.fn.dataTable.ext.search = []; // hapus filter custom sebelumnya
//             $.fn.dataTable.ext.search.push(function (settings, data, dataIndex) {
//                 const keyword = $('#ExtractionTable_filter input').val().trim().toLowerCase();
//                 if (!keyword) return true;

//                 for (let i = 0; i < data.length; i++) {
//                     if (data[i].toLowerCase() === keyword) {
//                         return true;
//                     }
//                 }
//                 return false;
//             });

//             // Pasang event agar search strict aktif saat user ketik
//             $('#ExtractionTable_filter input').off().on('input', function () {
//                 table.draw(); // trigger ulang filter strict
//             });
//         })
//         .catch(err => {
//             console.error("Gagal load extraction table:", err);
//         });
// }



// document.addEventListener("DOMContentLoaded", function () {
//     loadNewsTable();
//     loadExtractionTable();
// });

function loadNewsTable() {
    fetch('/load-combine-news')
        .then(res => res.json())
        .then(data => {
            const tbody = document.querySelector('#NewsTable tbody');
            tbody.innerHTML = '';

            data.forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td> 
                    <td>${row.news_id || ''}</td>
                    <td>${row.news_date || ''}</td>
                    <td><a href="${row.link || '#'}" target="_blank">Lihat</a></td>
                    <td>${row.title || ''}</td>
                    <td>${(row.content || '').slice(0, 200)}...</td>
                `;
                tbody.appendChild(tr);
            });

            const table = $('#NewsTable').DataTable({
                destroy: true,
                scrollX: false,
                paging: true,
                searching: true,
            });

            // Hapus filter lama untuk NewsTable
            $.fn.dataTable.ext.search = $.fn.dataTable.ext.search.filter(f => !(f._tableId === 'NewsTable'));

            // Tambahkan filter strict match khusus NewsTable
            const newsFilter = function (settings, data, dataIndex) {
                if (settings.nTable.id !== 'NewsTable') return true;

                const keyword = $('#NewsTable_filter input').val().trim().toLowerCase();
                if (!keyword) return true;

                for (let i = 0; i < data.length; i++) {
                    if (data[i].toLowerCase().includes(keyword)) {
                        return true;
                    }
                }
                return false;
            };
            newsFilter._tableId = 'NewsTable';
            $.fn.dataTable.ext.search.push(newsFilter);

            $('#NewsTable_filter input').off().on('input', function () {
                table.draw();
            });
        })
        .catch(err => {
            console.error("Gagal load news table:", err);
        });
}

function loadExtractionTable() {
    fetch('/load-extraction-news')
        .then(res => res.json())
        .then(data => {
            console.log("DATA LOADED:", data);

            const tbody = document.querySelector('#ExtractionTable tbody');
            if (!tbody) {
                console.error("Tbody tidak ditemukan!");
                return;
            }

            tbody.innerHTML = '';

            data.forEach((row, index) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${index + 1}</td> 
                    <td>${row.news_id || ''}</td>
                    <td>${row.LOC || ''}</td>
                    <td>${row.DAY || ''}</td>
                    <td>${row.DATE_STANDARDIZED || ''}</td>
                    <td>${row.TIME || ''}</td>
                    <td>${row.VEHICLE || ''}</td>
                    <td>${row.MERK || ''}</td>
                    <td>${row.ROAD || ''}</td>
                    <td>${row.CAUSE || ''}</td>
                    <td>${row.ORG || ''}</td>
                    <td>${row.DRIVER_AGE || ''}</td>
                    <td>${row.VICTIM_AGE || ''}</td>
                    <td>${row.INJURY || ''}</td>
                    <td>${row.DEATH || ''}</td>
                `;
                tbody.appendChild(tr);
            });

            const table = $('#ExtractionTable').DataTable({
                destroy: true,
                scrollX: false,
                paging: true,
                searching: true,
            });

            // Hapus filter lama untuk ExtractionTable
            $.fn.dataTable.ext.search = $.fn.dataTable.ext.search.filter(f => !(f._tableId === 'ExtractionTable'));

            // Tambahkan filter strict match khusus ExtractionTable
            const extractionFilter = function (settings, data, dataIndex) {
                if (settings.nTable.id !== 'ExtractionTable') return true;

                const keyword = $('#ExtractionTable_filter input').val().trim().toLowerCase();
                if (!keyword) return true;

                for (let i = 0; i < data.length; i++) {
                    if (data[i].toLowerCase().includes(keyword)) {
                        return true;
                    }
                }
                return false;
            };
            extractionFilter._tableId = 'ExtractionTable';
            $.fn.dataTable.ext.search.push(extractionFilter);

            $('#ExtractionTable_filter input').off().on('input', function () {
                table.draw();
            });
        })
        .catch(err => {
            console.error("Gagal load extraction table:", err);
        });
}

document.addEventListener("DOMContentLoaded", function () {
    loadNewsTable();
    loadExtractionTable();
});
