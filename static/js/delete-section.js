let iconsVisible = false; // Track the visibility state of the icons

function toggleDeleteIcons() {
    const checkboxes = document.querySelectorAll('.section-checkbox');
    iconsVisible = !iconsVisible; // Toggle visibility state

    checkboxes.forEach(checkbox => {
        checkbox.style.display = iconsVisible ? 'block' : 'none'; // Show or hide the icons
    });

    const deleteButton = document.getElementById('deleteSelected');
    if (iconsVisible) {
        deleteButton.textContent = 'Cancel'; // Change button text to "Cancel"
    } else {
        deleteButton.textContent = 'Delete Selected'; // Revert button text
        resetSelections(); // Reset selections when hiding the icons
    }
}

function resetSelections() {
    // Optionally, reset any selections or UI elements related to the delete functionality
    const checkboxes = document.querySelectorAll('.section-checkbox');
    checkboxes.forEach(checkbox => {
        checkbox.style.display = 'none'; // Ensure all checkboxes are hidden
    });
}

function confirmDelete(sectionId) {
    if (confirm('Are you sure you want to delete this section?')) {
        const csrfToken = getCookie('csrftoken'); // Get CSRF token for authentication

        // Send DELETE request to the server for the selected section
        fetch(`/delete-section/${sectionId}/`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
        })
        .then(response => {
            if (response.ok) {
                // Remove the section from the DOM
                document.getElementById(`section-${sectionId}`).remove();
            } else {
                alert(`Failed to delete section ${sectionId}.`);
            }
        })
        .catch(error => {
            console.error('Error during fetch:', error);
            alert(`Error occurred while deleting section ${sectionId}: ${error}`);
        });
    }
}
