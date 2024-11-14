
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
                            <span class="comment-user"><strong>${data.comment.user} : </strong></span>
                            ${data.comment.is_solved ? 
                                '<span class="badge bg-success badge-custom">Solved</span>' :
                                `<i class="fa fa-check-circle text-muted check-icon" onclick="markCommentSolved(${data.comment.id}, this)" style="cursor: pointer; font-size: 1.2em;"></i>`}
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
            } else {
                console.error("Error:", data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    });
});
