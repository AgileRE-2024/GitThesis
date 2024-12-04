document.addEventListener("keydown", async (event) => {
    if (event.ctrlKey && event.key === "s") {
        event.preventDefault();

        const textarea = document.activeElement;
        if (textarea.tagName === "TEXTAREA" && textarea.classList.contains("editor-content")) {
            const projectID = document.getElementById("project-id").value;
            const sectionID = textarea.closest(".section-container").getAttribute("data-section-id");
            const updatedContent = textarea.value;

            try {
                const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]').value;
                const response = await fetch(`/project/${projectID}/update-section/${sectionID}/`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json",
                        "X-CSRFToken": csrfToken,
                    },
                    body: JSON.stringify({ content: updatedContent }),
                });

                const result = await response.json();

                if (response.ok) {
                    console.log("Section updated successfully:", result.message);
                } else {
                    console.error("Error updating section:", result.message || response.statusText);
                }
            } catch (error) {
                console.error("Failed to update section:", error);
            }
        }
    }
});
