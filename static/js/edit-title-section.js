function editTitle(element, sectionId) {
    const originalTitle = element.textContent;
    const input = document.createElement("input");
    input.type = "text";
    input.value = originalTitle;

    // Replace the button with the input field
    element.parentNode.replaceChild(input, element);
    input.focus();

    // Handle blur event to save title
    input.addEventListener("blur", () => {
        saveTitle(input, originalTitle, sectionId);
    });

    // Handle keypress event for Enter key
    input.addEventListener("keydown", (event) => {
        if (event.key === "Enter") {
            event.preventDefault(); // Prevent form submission if inside a form
            saveTitle(input, originalTitle, sectionId);
        }
    });
}

// Function to save the title and revert back to button
function saveTitle(input, originalTitle, sectionId) {
    const newTitle = input.value.trim();

    // If the title is not empty, update it
    if (newTitle) {
        // Make an AJAX call to save the new title (assuming you have a view for this)
        fetch(`/update-section-title/${sectionId}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': '{{ csrf_token }}' // Ensure CSRF token is included
            },
            body: JSON.stringify({ title: newTitle })
        })
        .then(response => {
            if (response.ok) {
                // Refresh the page to reflect the updated title
                window.location.reload();
            } else {
                alert("Error updating title.");
            }
        });
    } else {
        // If title is empty, revert back to original
        const newAnchor = document.createElement("a");
        newAnchor.className = "nav-item pt-1 pb-1 btn btn-outline-primary mt-3 text-dark fw-medium";
        newAnchor.href = `#${originalTitle|slugify}`;
        newAnchor.textContent = originalTitle;
        newAnchor.ondblclick = () => editTitle(newAnchor, sectionId);
        input.parentNode.replaceChild(newAnchor, input);
    }
}
