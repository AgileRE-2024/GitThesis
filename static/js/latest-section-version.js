
// Fungsi untuk mendapatkan section yang sedang terlihat di viewport
function getCurrentSection() {
    const sections = document.querySelectorAll('[id^="section-content-"]'); // Sesuaikan dengan ID prefix section content Anda
    let currentSection = null;
    let closestDistance = Infinity;

    sections.forEach(section => {
        const rect = section.getBoundingClientRect();
        const distanceFromTop = Math.abs(rect.top);
        
        // Update currentSection jika section ini lebih dekat ke viewport top
        if (distanceFromTop < closestDistance) {
            closestDistance = distanceFromTop;
            currentSection = section;
        }
    });

    return currentSection;
}

// Tambahkan throttle untuk mencegah terlalu banyak panggilan saat scroll
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    }
}

// Event listener untuk scroll
window.addEventListener('scroll', throttle(function() {
    const currentSection = getCurrentSection();
    if (currentSection) {
        const sectionId = currentSection.getAttribute('data-section-id'); // Pastikan setiap section content memiliki data-section-id
        
        // Update active class pada sidebar
        document.querySelectorAll('.section-query').forEach(section => {
            section.classList.remove('active');
            if (section.getAttribute('data-id') === sectionId) {
                section.classList.add('active');
            }
        });

        // Update version list
        loadSectionVersion(sectionId);

        // Update URL tanpa memicu scroll
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('section_id', sectionId);
        window.history.replaceState({}, '', newUrl);
    }
}, 200)); // Throttle 200ms

// Fungsi untuk memuat riwayat perubahan saat section terlihat
function loadSectionVersion(sectionId) {
    // Menampilkan loading message sebelum data dimuat
    const loadingMessage = document.getElementById("loading-message");
    loadingMessage.style.display = "block";
    document.getElementById("section-versions-list").innerHTML = "";

    // Menggunakan AJAX untuk memanggil data versi dari server
    fetch(`/get_section_versions/${sectionId}/`)
        .then(response => response.json())
        .then(data => {
            // Menyembunyikan loading message setelah data dimuat
            loadingMessage.style.display = "none";
            
            // Menyiapkan HTML untuk versi section
            let sectionVersionHtml = '';

            // Menambahkan link untuk menuju halaman detail versi section
            

            if (data.section_versions.length > 0) {
                data.section_versions.forEach(version => {
                    sectionVersionHtml += `
                        <h6 class="card-title">${version.title}</h6>
                        <p class="text-muted mt-2">${version.created_at}</p>

                        <a href="/myprojects/section-versions/${sectionId}/" class="btn btn-primary btn-sm">
                            All Section Histories
                        </a>
                    `;
                });
            } else {
                sectionVersionHtml = '<p class="text-muted">No changes yet.</p>';
            }

            

            // Memperbarui isi dengan data baru
            document.getElementById("section-versions-list").innerHTML = sectionVersionHtml;
        })
        .catch(error => {
            console.error("Error loading section versions:", error);
            document.getElementById("section-version").innerHTML = "Error loading section version.";
        });
}
