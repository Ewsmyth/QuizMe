document.getElementById('startQuizBtn').addEventListener('click', async () => {
    try {
        console.log("Quiz ID before sending request:", quizId);

        // Fetch the CSRF token
        const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

        // Send the POST request
        const response = await fetch(`/user-home/quiz/${quizId}/start`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error("Response status:", response.status);
            console.error("Response body:", errorText);
            throw new Error("Failed to start quiz");
        }

        const data = await response.json();
        console.log("Response data:", data);

        // Redirect if redirect_url is provided
        if (data.redirect_url) {
            window.location.href = data.redirect_url;
        } else {
            console.error("Redirect URL missing in response");
            alert("Failed to redirect. Please try again.");
        }
    } catch (error) {
        console.error("Error starting quiz:", error);
        alert("Failed to start quiz. Please try again.");
    }
});
