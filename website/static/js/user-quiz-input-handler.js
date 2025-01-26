// Track user answers
const userAnswers = {};

// Event handler for storing user answers
function storeAnswer(questionIndex, value, isCheckbox = false) {
    if (isCheckbox) {
        // Handle multiple answers for checkboxes
        if (!userAnswers[questionIndex]) {
            userAnswers[questionIndex] = [];
        }
        if (userAnswers[questionIndex].includes(value)) {
            // Remove value if unchecked
            userAnswers[questionIndex] = userAnswers[questionIndex].filter((v) => v !== value);
        } else {
            // Add value if checked
            userAnswers[questionIndex].push(value);
        }
    } else {
        // Handle single answer for radio buttons or textarea
        userAnswers[questionIndex] = value;
    }
    console.log("User answers updated:", userAnswers);
}

// Attach event listeners to inputs
document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".carousel-item").forEach((item, index) => {
        // Handle radio and checkbox inputs
        item.querySelectorAll("input[type='radio'], input[type='checkbox']").forEach((input) => {
            input.addEventListener("change", (event) => {
                const value = event.target.value;
                const isCheckbox = event.target.type === "checkbox";
                storeAnswer(index, value, isCheckbox);
            });
        });

        // Handle textarea inputs
        const textarea = item.querySelector("textarea");
        if (textarea) {
            textarea.addEventListener("input", (event) => {
                const value = event.target.value;
                storeAnswer(index, value);
            });
        }
    });
});
