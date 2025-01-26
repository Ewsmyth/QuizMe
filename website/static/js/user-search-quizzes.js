async function fetchQuizzes(searchTerm = "") {
    try {
        const response = await fetch(`/api/quizzes?search=${encodeURIComponent(searchTerm)}`);
        if (!response.ok) {
            throw new Error("Failed to fetch quizzes");
        }
        const data = await response.json();
        renderQuizzes(data.quizzes);
    } catch (error) {
        console.error("Error fetching quizzes:", error);
    }
}

function renderQuizzes(quizzes) {
    const quizList = document.getElementById("quizList");
    quizList.innerHTML = ""; // Clear previous list

    if (quizzes.length === 0) {
        quizList.innerHTML = "<p>No quizzes found</p>";
        return;
    }

    quizzes.forEach(quiz => {
        const quizElement = document.createElement("div");
        quizElement.classList.add("quiz-item");
        quizElement.innerHTML = `
            <h2>${quiz.quiz}</h2>
            <p>${quiz.quizDescription}</p>
            <a href="/user-home/start-quiz/${quiz._id}" class="quiz-link">Select Quiz</a>
        `;
        quizList.appendChild(quizElement);
    });
}

function filterQuizzes() {
    const searchInput = document.getElementById("quizSearch");
    const searchTerm = searchInput.value;
    fetchQuizzes(searchTerm);
}

// Load all quizzes on page load
window.onload = () => {
    fetchQuizzes();
};
