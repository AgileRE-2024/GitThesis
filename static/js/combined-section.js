document.getElementById('combined-form').addEventListener('submit', function(event) {
    event.preventDefault(); // Mencegah submit normal form
    
    const formData = new FormData(this);
    
    // Ambil elemen tombol dan loading indicator
    const generateButton = document.getElementById('generate-pdf-btn');
    const loadingIndicator = document.getElementById('loading-indicator');
    
    // Sembunyikan tombol dan tampilkan loading indicator
    generateButton.style.display = 'none'; // Sembunyikan tombol
    loadingIndicator.style.display = 'block'; // Tampilkan loading indicator

    // Gunakan requestAnimationFrame untuk memastikan UI memperbarui sebelum fetch
    requestAnimationFrame(() => {
        setTimeout(() => {
            // Panggil fetch dalam fungsi terpisah untuk menghindari blocking UI
            submitFormData(formData, this.action, loadingIndicator, generateButton);
        }, 100); // Delay 2 detik sebelum fetch
    });
});

function submitFormData(formData, actionUrl, loadingIndicator, generateButton) {
    fetch(actionUrl, {
        method: 'POST',
        body: formData,
        headers: {
            "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
        }
    })
    .then(response => {
        if (response.ok) {
            return response.json(); // Mengharapkan JSON yang berisi URL PDF
        }
        throw new Error('PDF generation failed');
    })
    .then(data => {
        // Sembunyikan loading indicator setelah selesai
        loadingIndicator.style.display = 'none';
        generateButton.style.display = 'block'; // Tampilkan kembali tombol
        
        if (data.pdf_url) {
            window.open(data.pdf_url, '_blank');
        } else {
            throw new Error('PDF generation failed');
        }
    })
    .catch(error => {
        console.error(error);
        loadingIndicator.style.display = 'none'; // Sembunyikan loading indicator
        generateButton.style.display = 'block'; // Tampilkan kembali tombol
        alert(error.message);
    });
}
