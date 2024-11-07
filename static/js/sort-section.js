document.addEventListener('DOMContentLoaded', function() {
    var sortable = Sortable.create(document.getElementById('section-list'), {
        animation: 150,
        onEnd: function (evt) {
            console.log("Section order changed. Click 'Update Position' to save changes.");
            
            // Update data-position attributes after drag
            const sections = document.querySelectorAll('li.section-query[id^="section-"]');
            sections.forEach((section, index) => {
                // Index + 1 karena position dimulai dari 1, bukan 0
                section.setAttribute('data-position', index + 1);
                console.log(`Updated ${section.id} position to ${index + 1}`);
            });
        }
    });

    var updateButton = document.getElementById('update-position-btn');
    if (updateButton) {
        updateButton.addEventListener('click', function() {
            console.log("Button clicked");

            // Explicitly exclude the "No sections available" element by checking for section-query class
            const sections = document.querySelectorAll('li.section-query[id^="section-"]');
            console.log("Found valid sections:", sections.length);

            let order = [];
            
            sections.forEach((section) => {
                // Log the current section element for debugging
                console.log("Processing section:", section.outerHTML);
                
                // Get the section ID and position
                let sectionId = section.id.replace('section-', '');
                let position = section.getAttribute('data-position');
                
                console.log("Extracted data:", {
                    sectionId: sectionId,
                    position: position
                });

                if (sectionId && position && !isNaN(parseInt(sectionId)) && !isNaN(parseInt(position))) {
                    order.push({
                        id: parseInt(sectionId),
                        position: parseInt(position)
                    });
                    console.log("Added to order:", {
                        id: parseInt(sectionId),
                        position: parseInt(position)
                    });
                }
            });

            console.log("Final order array:", order);
            
            const projectId = document.getElementById("project-id").value;

            console.log("porjectid:", projectId)
            
            if (order.length > 0) {
                updateSectionOrder(order, projectId);
            } else {
                console.log("No valid sections to update.");
            }
        });
    } else {
        console.error("Update button not found in the DOM.");
    }
});

function updateSectionOrder(order, projectId) {
    var csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

    // Log the exact request payload
    const requestData = {
        sections: order // Wrapped in 'sections' key
    };
    
    console.log("Sending request with data:", JSON.stringify(requestData, null, 2));

    fetch(`/project/${projectId}/update-section-order/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrfToken
        },
        body: JSON.stringify(requestData)
    })
    .then(response => {
        // First check if response is ok
        if (!response.ok) {
            // Log the raw response for debugging
            return response.text().then(text => {
                console.error('Server response:', text);
                throw new Error(`HTTP error! status: ${response.status}`);
            });
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            console.log("Section order updated successfully");
            showSuccessMessage("Section order updated successfully");
            // Optional: Refresh the page or update the UI
            window.location.reload();
        } else {
            console.error("Server returned error:", data);
            showErrorMessage(data.error || "Failed to update section order");
        }
    })
    .catch(error => {
        console.error("Request failed:", error);
        showErrorMessage("An error occurred while updating section order. Please check the console for details.");
    });
}

function showSuccessMessage(message) {
    // You might want to replace this with a better UI notification
    alert(message);
}

function showErrorMessage(message) {
    // You might want to replace this with a better UI notification
    alert(message);
}