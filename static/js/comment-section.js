document.addEventListener("DOMContentLoaded", function() {
    const commentForm = document.getElementById("commentForm");
    const commentList = document.getElementById("comment-list");
    let lastUpdatedSectionId = null;

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

    // Fungsi untuk update comments
    function updateComments(sectionId) {
        commentList.innerHTML = '<p>Loading comments...</p>';
    
        fetch(`/myprojects/get_comments/${sectionId}/`)
            .then(response => response.json())
            .then(data => {
                commentList.innerHTML = '';
    
                if (data.comments && data.comments.length > 0) {
                    data.comments.forEach(comment => {
                        const commentItemHTML = `
                            <div class="comment-item mb-2">
                                <div class="d-flex justify-content-between align-items-center">
                                    <span class="comment-user"><strong>${comment.user} : </strong></span>
                                    ${comment.is_solved ? 
                                        '<span class="badge bg-success badge-custom">Solved</span>' :
                                        `<i class="fa fa-check-circle text-muted" onclick="markCommentSolved(${comment.id}, this)" style="cursor: pointer; font-size: 1.2em;"></i>`}
                                </div>
                                <div class="comment-text mt-1">
                                    ${comment.content}
                                </div>
                            </div>
                        `;
                        commentList.insertAdjacentHTML("beforeend", commentItemHTML);
                    });
                } else {
                    commentList.innerHTML = '<p>Tidak ada komentar untuk section ini.</p>';
                }
            })
            .catch(error => {
                console.error("Error:", error);
                commentList.innerHTML = '<p>Error loading comments. Please try again.</p>';
            });
    }
    

    // Fungsi untuk menandai komentar sebagai "solved"
    window.markCommentSolved = function(commentId, iconElement) {
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
                iconElement.parentElement.innerHTML = '<span class="badge bg-success ms-1">Solved</span>';
            } else {
                alert(data.message || 'Error marking comment as solved');
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    };
    


});
