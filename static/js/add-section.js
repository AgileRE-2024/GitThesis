function addSection() {
    console.log("Creating a new section input and save button...");
    
    const newSectionInput = document.createElement("input");
    newSectionInput.type = "text";
    newSectionInput.placeholder = "Masukkan Judul Section Baru";
    newSectionInput.className = "form-control mt-2";
    
    const saveButton = document.createElement("button");
    saveButton.textContent = "Add";
    saveButton.className = "btn btn-primary mt-2";
    
    const saveNewSection = () => {
        console.log("Save button clicked or Enter key pressed.");
        const newTitle = newSectionInput.value.trim();
        const projectId = document.getElementById("project-id").value;  // Ambil project ID dari input hidden
        console.log("New section title:", newTitle);  
        console.log("Project ID:", projectId);  // Pastikan project ID diambil dengan benar

        if (newTitle && projectId) {
            console.log("Sending AJAX request to save the new section...");
            fetch('/add-section/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')  // Ambil token CSRF
                },
                body: JSON.stringify({ title: newTitle, project_id: projectId })  // Kirim project_id
            })
            .then(response => {
                console.log("Response received from server:", response);
                if (response.ok) {
                    console.log("Section added successfully, refreshing the page...");
                    window.location.reload();
                } else {
                    console.error("Error adding section:", response.statusText);
                    alert("Error adding section: " + response.statusText);
                }
            })
            .catch(error => {
                console.error("Error occurred during fetch:", error);
                alert("Error occurred: " + error);
            });
        } else {
            console.warn("Judul section atau project ID tidak boleh kosong.");
            alert("Judul section atau project ID tidak boleh kosong.");
        }
    };

    saveButton.onclick = saveNewSection;

    newSectionInput.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault();
            saveNewSection();
        }
    });

    const listContainer = document.querySelector(".list-unstyled");
    listContainer.appendChild(newSectionInput);
    listContainer.appendChild(saveButton);

    // Tampilkan tombol "Cancel" setelah klik "Add Section"
    const cancelButton = document.getElementById("cancelSection");
    if (cancelButton) {
        cancelButton.style.display = "inline-block";
    }

    // Sembunyikan tombol "Add Section" saat section baru ditambahkan
    const addSectionButton = document.querySelector(".btn-primary.btn-sm.mt-1.mb-1");
    if (addSectionButton) {
        addSectionButton.style.display = "none";
    }
}

// Fungsi untuk mengambil CSRF token dari cookie
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            // Apakah cookie ini dimulai dengan nama yang kita cari?
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// cancel add section
function cancelAddSection() {
    // Hapus elemen input untuk judul section baru dan tombol "Add"
    const newSectionInput = document.querySelector(".list-unstyled input.form-control.mt-2");
    const saveButton = document.querySelector(".list-unstyled button.btn.btn-primary.mt-2");

    if (newSectionInput) {
        newSectionInput.remove();
    }

    if (saveButton) {
        saveButton.remove();
    }

    // Sembunyikan tombol "Cancel" setelah cancel
    const cancelButton = document.getElementById('cancelSection');
    if (cancelButton) {
        cancelButton.style.display = 'none';
    }
    
    // Tampilkan tombol "Add Section" kembali jika dibutuhkan
    const addSectionButton = document.querySelector(".btn-primary.btn-sm.mt-1.mb-1");
    if (addSectionButton) {
        addSectionButton.style.display = 'inline-block';
    }
}
