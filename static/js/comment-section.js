document.addEventListener("DOMContentLoaded", function() {
    const commentList = document.getElementById("comment-list");
    let lastUpdatedSectionId = null;

    // Inisialisasi tooltip Bootstrap untuk elemen yang sudah ada
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element);
    });

    // Fungsi untuk mendapatkan section yang sedang terlihat di viewport
    function getCurrentSection() {
        const sections = document.querySelectorAll('[id^="section-content-"]');
        let currentSection = null;
        let closestDistance = Infinity;

        sections.forEach(section => {
            const rect = section.getBoundingClientRect();
            const distanceFromTop = Math.abs(rect.top);
            
            if (distanceFromTop < closestDistance) {
                closestDistance = distanceFromTop;
                currentSection = section;
            }
        });

        return currentSection;
    }

    // Fungsi throttle untuk mencegah terlalu banyak panggilan saat scroll
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
            const sectionId = currentSection.getAttribute('data-section-id');
            
            // Update active class pada sidebar
            document.querySelectorAll('.section-query').forEach(section => {
                section.classList.remove('active');
                if (section.getAttribute('data-id') === sectionId) {
                    section.classList.add('active');
                }
            });

            // Update comments hanya jika section berubah
            if (lastUpdatedSectionId !== sectionId) {
                updateComments(sectionId);
                lastUpdatedSectionId = sectionId;
                document.getElementById("current-section-id").value = sectionId;
            }
        }
    }, 200));

  
    // Mengatur format waktu dengan locale id-ID (Indonesia) sesuai format yang diminta
    function formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric',
            hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
        }).replace(",", ""); // Menghilangkan koma setelah hari
    }

    // Fungsi untuk menandai komentar sebagai "solved"
    window.markCommentSolved = function(commentId, iconElement) {
        // Hapus tooltip sebelum mengirim request
        const tooltipInstance = bootstrap.Tooltip.getInstance(iconElement);
        if (tooltipInstance) tooltipInstance.dispose();
    
        fetch(`/comments/mark_solved/${commentId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': document.querySelector("[name=csrfmiddlewaretoken]").value,
                'Content-Type': 'application/json'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'success') {
                const commentItem = iconElement.closest('.comment-item');
                const statusDiv = commentItem.querySelector('.d-flex.justify-content-between');
                const createdAt = formatDate(new Date(data.created_at));
                const commentUsername = commentItem.querySelector('.comment-user').textContent.trim();
                const solvedByUsername = data.solved_by;  // Dari server
                const solvedAt = formatDate(new Date(data.solved_at)); // Waktu dari server
    
                // Tambahkan badge Solved
                statusDiv.insertAdjacentHTML('beforeend', `
                    <span class="badge bg-success badge-custom" 
                        data-bs-toggle="tooltip" 
                        title="Commented by: ${commentUsername} on ${createdAt} | Solved by: ${solvedByUsername} on ${solvedAt}">
                        
                        Solved
                    </span>
                `);
    
                // Inisialisasi ulang tooltip untuk badge baru
                const badge = statusDiv.querySelector('.badge');
                new bootstrap.Tooltip(badge, { placement: 'end', delay: { show: 200, hide: 200 } });
    
                // Hapus ikon solved
                iconElement.remove();
                initializeTooltips();
            } else {
                alert(data.message || 'Error marking comment as solved');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };

    // Fungsi untuk memperbarui komentar (menarik komentar baru untuk setiap section)
    window.updateComments = function(sectionId) {
        commentList.innerHTML = '<p>Loading comments...</p>';

        fetch(`/myprojects/get_comments/${sectionId}/`)
            .then(response => response.json())
            .then(data => {
                commentList.innerHTML = '';

                if (data.comments && data.comments.length > 0) {
                    data.comments.forEach(comment => {
                        const solvedInfo = comment.is_solved
                            ? `<span class="badge bg-success badge-custom" 
                                data-bs-toggle="tooltip" 
                                title="Commented by: ${comment.user} on ${formatDate(comment.created_at)}\n | Solved by: ${comment.solved_by || 'N/A'} on ${formatDate(comment.solved_at)}">
                                Solved
                            </span>`
                            : `<i class="fa fa-check-circle text-muted" 
                                onclick="markCommentSolved(${comment.id}, this)" 
                                style="cursor: pointer; font-size: 1.2rem;" 
                                data-bs-toggle="tooltip"
                                title="Click to mark as solved">
                            </i>`;

                            const commentItemHTML = `
                            <div class="comment-item mb-2">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="comment-user" data-user-name="${comment.user}" data-created-at="${formatDate(comment.created_at)}"><strong>${comment.user}:</strong></span>
                                    ${solvedInfo}
                                </div>
                                <div class="comment-text mt-1">
                                    ${comment.content}
                                </div>
                            </div>
                        `;
                        commentList.insertAdjacentHTML("beforeend", commentItemHTML);
                    });


                } else {
                    commentList.innerHTML = '<p>There are no comments for this section.</p>';
                }

                // Inisialisasi ulang tooltip
                initializeTooltips();  // Inisialisasi tooltip untuk komentar yang baru dimuat

                commentList.scrollTop = commentList.scrollHeight;
            })
            .catch(error => {
                console.error("Error:", error);
                commentList.innerHTML = '<p>Error loading comments. Please try again.</p>';
            });
    }

    const initialSection = getCurrentSection();
    if (initialSection) {
        const sectionId = initialSection.getAttribute('data-section-id');
        if (sectionId) {
            updateComments(sectionId);
            lastUpdatedSectionId = sectionId;
        }
    }

    // Fungsi untuk menginisialisasi tooltip
    function initializeTooltips() {
        const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
        tooltipElements.forEach(element => {
            new bootstrap.Tooltip(element, { placement: 'left' });
        });
    }

});