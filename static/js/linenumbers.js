// linenumbers.js

function updateLineNumbers(textarea, lineNumbers) {
    if (!textarea || !lineNumbers) return;  // Pengecekan jika elemen tidak ditemukan

    const lines = textarea.value.split("\n").length;
    lineNumbers.innerHTML = "";

    for (let i = 1; i <= lines; i++) {
        lineNumbers.innerHTML += i + "<br>";
    }

    // Sesuaikan tinggi textarea dan line numbers
    textarea.style.height = 'auto';
    textarea.style.height = textarea.scrollHeight + 'px';
    lineNumbers.style.height = textarea.scrollHeight + 'px';
}

// Inisialisasi line numbers untuk setiap section
document.querySelectorAll(".section-container").forEach((container, index) => {
    const textarea = container.querySelector(".editor-content");
    const lineNumbers = container.querySelector(".line-numbers");

    console.log(`Initializing section ${index + 1}`);

    if (textarea && lineNumbers) {
        updateLineNumbers(textarea, lineNumbers);

        textarea.addEventListener('input', () => updateLineNumbers(textarea, lineNumbers));
        textarea.addEventListener('scroll', () => {
            lineNumbers.scrollTop = textarea.scrollTop;
        });
    } else {
        console.error("Textarea atau line-numbers tidak ditemukan pada section", index + 1);
    }
});
