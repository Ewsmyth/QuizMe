document.addEventListener("DOMContentLoaded", async function () {
    const quizCreationForm = document.getElementById("quizCreationForm");
    const groupSelector = document.getElementById("groupSelector");

    // Fetch and populate group options
    async function fetchGroups() {
        try {
            const response = await fetch("/admin-home/get-groups/");
            const groups = await response.json();
            groupSelector.innerHTML = ""; // Clear existing options
            groups.forEach(group => {
                const option = document.createElement("option");
                option.value = group._id;
                option.textContent = group.name;
                groupSelector.appendChild(option);
            });
        } catch (error) {
            console.error("Error fetching groups:", error);
            alert("Failed to load groups. Please refresh the page.");
        }
    }

    // Fetch groups on page load
    await fetchGroups();

    // Handle form submission
    quizCreationForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = gatherFormData();
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;

        try {
            const response = await fetch("/admin-home/create-quiz/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            if (response.ok) {
                alert("Quiz created successfully!");
                quizCreationForm.reset(); // Reset the form
            } else {
                alert(result.error || "An error occurred while creating the quiz.");
            }
        } catch (error) {
            console.error("Error during quiz creation:", error);
            alert("An error occurred while creating the quiz.");
        }
    });

    // Gather form data
    function gatherFormData() {
        const quizName = document.getElementById("quizName").value.trim();
        const quizDescription = document.getElementById("quizDescription").value.trim();
        const quizSize = parseInt(document.getElementById("quizSize").value, 10);
        const groupIds = Array.from(groupSelector.selectedOptions).map(option => option.value);

        return {
            quiz: quizName,
            quizDescription,
            quizSize,
            groups: groupIds
        };
    }
});
