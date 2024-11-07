
document.addEventListener("keydown", async (event) => {
    if (event.ctrlKey && event.key === "s") {
        event.preventDefault();

        const textarea = document.activeElement;
        if (textarea.tagName === "TEXTAREA" && textarea.classList.contains("editor-content")) {
            const projectID = document.getElementById("project-id").value;
            const sectionID = textarea.closest(".section-container").getAttribute("data-section-id");
            const updatedContent = textarea.value;

            try {
                const response = await fetch(`/project/${projectID}/update-section/${sectionID}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": document.querySelector('[name=csrfmiddlewaretoken]').value,
                    },
                    body: JSON.stringify({ content: updatedContent }),
                });

                const result = await response.json(); // Mendapatkan respons dalam bentuk JSON

                if (response.ok) {
                    console.log("Section updated successfully.");
                } else {
                    console.error("Error updating section:", response.statusText);
                }
            } catch (error) {
                console.error("Failed to update section:", error);
            }
        }
    }
});
