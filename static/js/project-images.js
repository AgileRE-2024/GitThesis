    document.getElementById('custom-upload-button').addEventListener('click', function() {
        console.log("Custom upload button clicked.");
        document.getElementById('image-upload').click();
    });

    // Automatically upload the file when selected
    document.getElementById('image-upload').addEventListener('change', function() {
        const fileInput = document.getElementById('image-upload');
        if (fileInput.files.length === 0) {
            console.error("No file selected.");
            return;
        }

        const formData = new FormData();
        formData.append('image', fileInput.files[0]);

        // Ambil CSRF token dari cookie atau meta tag
        const csrfToken = document.querySelector('input[name="csrfmiddlewaretoken"]').value;  // Mengambil dari input hidden
        console.log("CSRF Token:", csrfToken);  // Debugging: Tampilkan nilai CSRF token

        const uploadUrl = document.getElementById('custom-upload-button').getAttribute('data-upload-url');
        console.log("Uploading to:", uploadUrl);

        fetch(uploadUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrfToken  // Gunakan CSRF token yang diambil
            }
        })
        .then(response => {
            console.log("Response received:", response);
            if (!response.ok) {
                throw new Error('HTTP error! status: ' + response.status);
            }
            return response.json();
        })
        .then(data => {
            console.log("Data received from server:", data);
            if (data.success) {
                alert('Image uploaded successfully');
                setTimeout(() => {
                    location.reload();  // Refresh halaman setelah alert ditutup
                }, 100); //
            } else {
                alert('Image upload failed: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error during upload:', error);
            alert('Error during upload: ' + error.message);
        });
    });
