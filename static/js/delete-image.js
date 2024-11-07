function deleteImage(imageId) {
    if (confirm("Are you sure you want to delete this image?")) {
        const csrfToken = getCookie('csrftoken');  // Ambil CSRF token untuk otentikasi

        // Kirim request ke server untuk menghapus gambar berdasarkan imageId
        fetch(`/delete-image/${imageId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken  // Sertakan CSRF token
            },
        })
        .then(response => {
            if (response.ok) {
                // Jika sukses, hapus elemen gambar dari DOM
                document.getElementById('image-' + imageId).remove();
            } else {
                alert('Failed to delete the image.');
            }
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            alert('Error occurred while deleting image: ' + error);
        });
    }
}
