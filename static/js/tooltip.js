document.addEventListener("DOMContentLoaded", function () {
    // Bersihkan tooltip lama
    document.querySelectorAll('.tooltip').forEach(tooltip => tooltip.remove());

    // Inisialisasi tooltip baru
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element, {
            offset: [0, 10],
        });
    });
});
