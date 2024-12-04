// Mengatur format waktu dengan locale id-ID (Indonesia)
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-US', {
        year: 'numeric', month: 'long', day: 'numeric',
        hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false
    }).replace(",", ""); // Menghilangkan koma setelah hari
}

document.addEventListener("DOMContentLoaded", function() {
    const commentForm = document.getElementById("commentForm");
    const commentList = document.getElementById("comment-list");

    // Fungsi untuk menambahkan komentar    
    commentForm.addEventListener("submit", function(e) {
        e.preventDefault();
    
        const formData = new FormData(this);
        
        fetch(addCommentUrl, {
            method: "POST",
            body: formData,
            headers: {
                "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Reset form
                commentForm.reset();

                // Menambahkan komentar baru ke daftar komentar
                const newCommentHTML = `
                    <div class="comment-item mb-2" data-comment-id="${data.comment.id}">
                        <div class="d-flex justify-content-between align-items-center">
                            <span class="comment-user"><strong>${data.comment.user}:</strong></span>
                            ${data.comment.is_solved 
                                ? `<span class="badge bg-success badge-custom" 
                                    data-bs-toggle="tooltip" 
                                    title="Commented by: ${data.comment.user} on ${formatDate(data.comment.created_at)}\nSolved by: ${data.comment.solved_by} on ${formatDate(data.comment.solved_at)}">
                                    Solved
                                </span>` 
                                : `<i class="fa fa-check-circle text-muted check-icon" 
                                    style="cursor: pointer; font-size: 1.2rem;" 
                                    data-bs-toggle="tooltip" 
                                    title="Click to mark as solved">
                                </i>`}
                        </div>
                        <div class="comment-text mt-1">
                            ${data.comment.content}
                        </div>
                    </div>
                `;

                // Cek apakah masih ada pesan "There are no comments for this section"
                const noCommentsMessage = commentList.querySelector('p');
                if (noCommentsMessage) {
                    noCommentsMessage.remove();  // Hapus pesan tidak ada komentar
                }

                // Menambahkan komentar baru ke dalam commentList
                commentList.insertAdjacentHTML("beforeend", newCommentHTML);

                const currentSectionId = document.getElementById("current-section-id").value;
                window.updateComments(currentSectionId);

                // Inisialisasi tooltip pada elemen baru
                initializeTooltips(); // Fungsi ini menginisialisasi tooltip untuk elemen baru

                commentList.scrollTop = commentList.scrollHeight;
            } else {
                console.error("Error:", data.message);
            }

        })
        .catch(error => console.error("Error:", error));
    });
});

// Fungsi untuk menginisialisasi tooltip
function initializeTooltips() {
    // Menginisialisasi tooltip pada elemen baru yang ditambahkan
    const tooltipElements = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipElements.forEach(element => {
        new bootstrap.Tooltip(element, { placement: 'top' });
    });
}
