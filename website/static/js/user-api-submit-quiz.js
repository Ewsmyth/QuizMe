async function handleSubmit(event, token) {
    event.preventDefault(); // Prevent the default form submission

    const form = event.target;
    const formData = new FormData(form);

    // Extract CSRF token from the form
    const csrfToken = form.querySelector('input[name="csrf_token"]').value;

    // Convert FormData to JSON object
    const data = {};
    formData.forEach((value, key) => {
        if (key === "question_ids[]") {
            if (!data.question_ids) {
                data.question_ids = [];
            }
            data.question_ids.push(value);
        } else {
            if (data[key]) {
                if (Array.isArray(data[key])) {
                    data[key].push(value);
                } else {
                    data[key] = [data[key], value];
                }
            } else {
                data[key] = value;
            }
        }
    });

    try {
        // Send the data to the API
        const response = await fetch(`/api/submit-quiz/${token}/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Include the CSRF token in the headers
            },
            body: JSON.stringify(data), // Send JSON data
        });

        if (response.redirected) {
            // Handle backend redirect
            window.location.href = response.url;
        } else {
            const error = await response.json();
            alert(`Failed to submit the quiz: ${error.message}`);
        }
    } catch (error) {
        console.error("Error:", error);
        alert("An error occurred while submitting the quiz.");
    }
}
