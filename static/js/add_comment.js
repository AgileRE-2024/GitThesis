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
                    <div class="comment-item d-flex justify-content-between align-items-center mb-2" data-comment-id="${data.comment.id}">
                        <div class="d-flex flex-grow-1 align-items-center">
                            <strong class="comment-user me-2">${data.comment.user} :</strong>
                            <span class="comment-text me-auto">${data.comment.content}</span>
                        </div>
                        <div class="comment-status">
                            ${data.comment.is_solved ? 
                                '<span class="badge bg-success badge-custom">Solved</span>' : 
                                `<i class="fa fa-check-circle text-muted" onclick="markCommentSolved(${data.comment.id}, this)" style="cursor: pointer; font-size: 1.2em;"></i>`
                            }
                        </div>
                    </div>
                `;

            
                commentList.insertAdjacentHTML("beforeend", newCommentHTML);
            } else {
                console.error("Error:", data.message);
            }
        })
        .catch(error => console.error("Error:", error));
    });
});
