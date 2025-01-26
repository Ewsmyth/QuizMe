document.addEventListener("DOMContentLoaded", function () {
    const groupCreationForm = document.querySelector(".group-creation-form-wrapper form");
    const groupNameInput = document.getElementById("groupCreationNameInput");
    const submitBtn = document.getElementById("groupCreationSubmitBtn");

    groupCreationForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent form from refreshing the page

        // Extract CSRF token
        const csrfToken = "{{ csrf_token() }}";

        // Get the group name
        const groupName = groupNameInput.value.trim();

        if (!groupName) {
            alert("Please provide a group name.");
            return;
        }

        try {
            // Make AJAX request to create group
            const response = await fetch("/admin-home/create-group/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken // Include CSRF token in header
                },
                body: JSON.stringify({ name: groupName })
            });

            const result = await response.json();

            if (response.ok) {
                alert(result.success);
                groupNameInput.value = ""; // Clear the input field
            } else {
                alert(result.error || "Failed to create group.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred while creating the group.");
        }
    });
});