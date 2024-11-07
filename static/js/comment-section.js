

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

        // Update comments
        updateComments(sectionId);
        
        // Update URL tanpa memicu scroll
        const newUrl = new URL(window.location);
        newUrl.searchParams.set('section_id', sectionId);
        window.history.replaceState({}, '', newUrl);
    }
}, 200)); // Throttle 200ms

// Modifikasi fungsi updateComments untuk mencegah update berulang
let lastUpdatedSectionId = null;

function updateComments(sectionId, event) {
    // Prevent default behavior if called from click event
    if (event) {
        event.preventDefault();
    }

    // Cek apakah section yang sama dengan update terakhir
    if (lastUpdatedSectionId === sectionId) {
        return; // Skip update jika section sama
    }

    lastUpdatedSectionId = sectionId;
    
    // Tampilkan loading state
    const commentList = document.getElementById('comment-list');
    commentList.innerHTML = '<p>Loading comments...</p>';
    
    fetch(`/myprojects/get_comments/${sectionId}/`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            // Cek lagi apakah masih section yang sama
            if (lastUpdatedSectionId !== sectionId) {
                return; // Skip update jika section sudah berubah
            }

            commentList.innerHTML = '';

            if (data.comments && data.comments.length > 0) {
                data.comments.forEach(comment => {
                    const commentItem = document.createElement('div');
                    commentItem.classList.add('comment-item');
                    commentItem.innerHTML = `
                        <div class="comment-content">
                            <strong>${comment.user} : </strong> <p>${comment.content}</p>
                        </div>
                    `;
                    commentList.appendChild(commentItem);
                });
            } else {
                commentList.innerHTML = '<p>Tidak ada komentar untuk section ini.</p>';
            }

            // Update section_id di form
            document.getElementById('current-section-id').value = sectionId;
           
        })
        .catch(error => {
            console.error('Error:', error);
            commentList.innerHTML = '<p>Error loading comments. Please try again.</p>';
        });
}

// Pastikan section content di HTML memiliki data-section-id
// Contoh:
// <div id="section-content-1" data-section-id="1" class="section-content">
//     <!-- Content -->
// </div>