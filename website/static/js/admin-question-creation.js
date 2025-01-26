document.addEventListener("DOMContentLoaded", async function () {
    const questionTypeSelector = document.getElementById("questionTypeSelector");
    const groupSelector = document.createElement("select");
    groupSelector.id = "groupSelector";
    const formContent = document.getElementById("questionFormContent");
    const questionCreationForm = document.getElementById("questionCreationForm");
    const createQuestionButton = document.getElementById("createQuestionButton");

    // Fetch and populate group names
    async function fetchGroups() {
        try {
            const response = await fetch("/admin-home/get-groups/");
            const groups = await response.json();
            groupSelector.innerHTML = "<option value=''>Select a group</option>";
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

    // Verify elements exist
    if (!questionTypeSelector || !formContent || !questionCreationForm || !createQuestionButton) {
        console.error("One or more required elements are missing. Check your HTML structure.");
        return;
    }

    // Insert group selector into the form
    questionTypeSelector.insertAdjacentElement("beforebegin", groupSelector);

    // Event listener for question type changes
    questionTypeSelector.addEventListener("change", function () {
        const questionType = questionTypeSelector.value;
        console.log("Question type changed:", questionType);
        renderForm(questionType);
    });

    // Initial render
    renderForm(questionTypeSelector.value);

    // Event listener for form submission
    questionCreationForm.addEventListener("submit", async function (event) {
        event.preventDefault(); // Prevent default form submission

        const formData = gatherFormData();
        const csrfToken = document.querySelector('input[name="csrf_token"]').value;

        try {
            const response = await fetch("/admin-home/create-question/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": csrfToken
                },
                body: JSON.stringify(formData)
            });

            const result = await response.json();
            if (response.ok) {
                alert("Question created successfully!");
                questionCreationForm.reset(); // Reset the form
                renderForm(questionTypeSelector.value); // Re-render the form
            } else {
                alert(result.error || "An error occurred while creating the question.");
            }
        } catch (error) {
            console.error("Error:", error);
            alert("An error occurred while creating the question.");
        }
    });

    function renderForm(type) {
        formContent.innerHTML = ""; // Clear existing form

        const questionTextarea = document.createElement("textarea");
        questionTextarea.placeholder = "Write your question here...";
        questionTextarea.classList.add("question-textarea");
        questionTextarea.name = "questionText";

        const questionFileInput = document.createElement("input");
        questionFileInput.type = "file";
        questionFileInput.classList.add("question-file-input");
        questionFileInput.name = "questionMedia";

        formContent.appendChild(questionTextarea);
        formContent.appendChild(questionFileInput);

        if (type === "multipleChoice" || type === "multipleAnswer") {
            renderOptions(type);
        } else if (type === "trueFalse") {
            renderTrueFalse();
        } else if (type === "openEnded") {
            renderOpenEnded();
        }
    }

    function renderOptions(type) {
        const optionsContainer = document.createElement("div");
        optionsContainer.id = "optionsContainer";

        addOptionInput(optionsContainer, type);

        const addButton = document.createElement("button");
        addButton.type = "button";
        addButton.textContent = "Add Option";
        addButton.addEventListener("click", () => addOptionInput(optionsContainer, type));

        formContent.appendChild(optionsContainer);
        formContent.appendChild(addButton);
    }

    function addOptionInput(container, type) {
        const optionWrapper = document.createElement("div");
        optionWrapper.classList.add("option-wrapper");

        const optionInput = document.createElement("input");
        optionInput.type = "text";
        optionInput.placeholder = "Option text";
        optionInput.name = "optionText";

        const optionFileInput = document.createElement("input");
        optionFileInput.type = "file";
        optionFileInput.name = "optionMedia";

        const correctInput = document.createElement("input");
        correctInput.type = type === "multipleChoice" ? "radio" : "checkbox";
        correctInput.name = "isCorrect";

        optionWrapper.appendChild(optionInput);
        optionWrapper.appendChild(optionFileInput);
        optionWrapper.appendChild(correctInput);
        container.appendChild(optionWrapper);
    }

    function renderTrueFalse() {
        const trueOption = createRadioOption("True");
        const falseOption = createRadioOption("False");

        formContent.appendChild(trueOption);
        formContent.appendChild(falseOption);
    }

    function createRadioOption(value) {
        const wrapper = document.createElement("div");
        const radio = document.createElement("input");
        radio.type = "radio";
        radio.name = "trueFalse";
        radio.value = value;

        const label = document.createElement("label");
        label.textContent = value;

        wrapper.appendChild(radio);
        wrapper.appendChild(label);

        return wrapper;
    }

    function renderOpenEnded() {
        const answerTextarea = document.createElement("textarea");
        answerTextarea.placeholder = "Write the textbook answer here...";
        answerTextarea.name = "openEndedAnswer";

        formContent.appendChild(answerTextarea);
    }

    function gatherFormData() {
        const groupId = document.getElementById("groupSelector").value;
        const questionType = document.getElementById("questionTypeSelector").value;
        const questionText = document.querySelector('textarea[name="questionText"]').value;
        const questionMedia = document.querySelector('input[name="questionMedia"]').files[0];
        let answerOptions = [];
        let correctAnswer = null;
    
        if (!groupId) {
            alert("Please select a group.");
            throw new Error("Group not selected.");
        }
    
        if (questionType === "multipleChoice" || questionType === "multipleAnswer") {
            const options = document.querySelectorAll("#optionsContainer .option-wrapper");
            options.forEach(option => {
                const text = option.querySelector('input[name="optionText"]').value;
                const media = option.querySelector('input[name="optionMedia"]').files[0];
                const isCorrect = option.querySelector('input[name="isCorrect"]').checked;
    
                answerOptions.push({
                    text,
                    media: media ? media.name : "",
                    isCorrect
                });
            });
        } else if (questionType === "trueFalse") {
            correctAnswer = document.querySelector('input[name="trueFalse"]:checked')?.value;
            if (!correctAnswer) {
                alert("Please select the correct answer (True/False).");
                throw new Error("Correct answer not selected.");
            }
        } else if (questionType === "openEnded") {
            correctAnswer = document.querySelector('textarea[name="openEndedAnswer"]').value;
            if (!correctAnswer) {
                alert("Please provide the correct answer for the open-ended question.");
                throw new Error("Correct answer not provided.");
            }
        }
    
        return {
            groupId,
            questionType,
            questionText,
            questionMedia: questionMedia ? questionMedia.name : "",
            answerOptions,
            correctAnswer
        };
    }    
});
