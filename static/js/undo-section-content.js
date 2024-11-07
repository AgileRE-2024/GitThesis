let activeSectionID = null; // Untuk menyimpan ID section aktif
const undoStack = [];
const redoStack = [];
let typingTimer;
const typingInterval = 300; // Menyimpan ke undoStack setelah 500ms tanpa input baru

// Set section aktif ketika textarea difokuskan
document.querySelectorAll("textarea.editor-content").forEach(textarea => {
    textarea.addEventListener("focus", function() {
        activeSectionID = this.closest(".section-container").getAttribute("data-section-id");
        console.log("Active Section ID set to:", activeSectionID);
    });
});

// Menyimpan state hanya setelah jeda
document.querySelectorAll("textarea.editor-content").forEach(textarea => {
    textarea.addEventListener("input", function() {
        clearTimeout(typingTimer);
        typingTimer = setTimeout(() => {
            if (activeSectionID) {
                undoStack.push(this.value); // Simpan konten setelah selesai mengetik
                redoStack.length = 0; // Kosongkan redoStack setiap ada perubahan baru
                console.log("Saved state to undoStack:", this.value);
            }
        }, typingInterval);
    });
});

// Undo (Ctrl + Z) dan Redo (Ctrl + Y atau Ctrl + Shift + Z) hanya di tampilan
document.addEventListener("keydown", (event) => {
    console.log(`Key pressed: ${event.key}, Ctrl: ${event.ctrlKey}, Shift: ${event.shiftKey}`); // Debug log

    // Undo (Ctrl + Z)
    if (event.ctrlKey && !event.shiftKey && event.key.toLowerCase === "z") {
        event.preventDefault();

        if (undoStack.length > 1) { // Memastikan ada lebih dari satu item
            redoStack.push(undoStack.pop()); // Simpan konten terakhir ke redoStack
            const previousContent = undoStack[undoStack.length - 1]; // Ambil konten terakhir
            document.activeElement.value = previousContent; // Kembalikan ke konten terakhir
            console.log("Undo successful to:", previousContent);
        } else {
            console.log("No more actions to undo.");
        }
    }

    // Redo (Ctrl + Y)
    if (event.ctrlKey && !event.shiftKey && event.key.toLowerCase === "y") {
        event.preventDefault();

        if (redoStack.length > 0) {
            const redoContent = redoStack.pop(); // Ambil konten dari redoStack
            undoStack.push(document.activeElement.value); // Simpan konten saat ini di undoStack
            document.activeElement.value = redoContent; // Kembalikan ke konten redo terakhir
            console.log("Redo successful to:", redoContent);
        } else {
            console.log("No more actions to redo.");
        }
    }

    // Redo (Ctrl + Shift + Z)
    if (event.ctrlKey && event.shiftKey && event.key.toLowerCase === "z") {
        event.preventDefault();

        if (redoStack.length > 0) {
            const redoContent = redoStack.pop(); // Ambil konten dari redoStack
            undoStack.push(document.activeElement.value); // Simpan konten saat ini di undoStack
            document.activeElement.value = redoContent; // Kembalikan ke konten redo terakhir
            console.log("Redo successful to:", redoContent);
        } else {
            console.log("No more actions to redo.");
        }
    }
});
