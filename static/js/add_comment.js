document.addEventListener("DOMContentLoaded", function() {
    const commentForm = document.getElementById("commentForm");
    const responseMessageDiv = document.getElementById("responseMessage");
    const commentList = document.querySelector(".comment-list");

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

                // Tambahkan komentar baru ke tampilan
                const newCommentHTML = `
                    <div class="comment-item" data-comment-id="${data.comment.id}">
                        <p><strong>${data.comment.user}:</strong> ${data.comment.content}</p>
                    </div>
                `;

                commentList.insertAdjacentHTML("beforeend", newCommentHTML);

                // Reset form setelah komentar berhasil ditambahkan
                commentForm.reset();

                // Tambah event listener untuk tombol hapus pada komentar baru
                // addDeleteEventListeners();
            } else {
                // Tampilkan pesan kesalahan
                // responseMessageDiv.innerHTML = `<div class="alert alert-danger">${data.message}</div>`;
            }
        })
        .catch(error => {
            console.error("Error:", error);
            // responseMessageDiv.innerHTML = `<div class="alert alert-danger">Terjadi kesalahan, silakan coba lagi.</div>`;
        });
    });

    // Fungsi untuk menambahkan event listener pada tombol hapus
    // function addDeleteEventListeners() {
    //     const deleteButtons = document.querySelectorAll(".delete-comment");
    //     deleteButtons.forEach(button => {
    //         button.addEventListener("click", function() {
    //             const commentItem = this.parentElement;
    //             commentItem.remove(); // Hapus komentar dari tampilan
    //         });
    //     });
    // }

    // // Tambahkan listener untuk tombol hapus saat halaman pertama kali dimuat
    // addDeleteEventListeners();

    
});
