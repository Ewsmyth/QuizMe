from flask import Blueprint, render_template, url_for, jsonify, g, redirect, session, request
from flask_login import current_user
from bson.json_util import dumps
from bson import ObjectId
from bson.errors import InvalidId
import random
from .auth import serializer, BadSignature
from flask_wtf.csrf import CSRFProtect
from datetime import datetime
import time

csrf = CSRFProtect()

# Store invalidated tokens in memory (or a database for production)
invalidated_tokens = set()

QUIZ_CACHE = {}
LOCK_DURATION = 600

user = Blueprint('user', __name__)

@user.route('/user-home/')
def user_home():
    return render_template('user-home.html')

@user.route('/user-home/learning')
def user_learning():
    return render_template('user-learning.html')

@user.route('/api/quizzes', methods=['GET'])
def get_quizzes():
    search_query = request.args.get('search', '').strip().lower()
    filters = {}
    if search_query:
        filters = {"quiz": {"$regex": search_query, "$options": "i"}}

    try:
        quizzes_cursor = g.mongo_db.quizzes.find(filters, {"quiz": 1, "quizDescription": 1, "quizSize": 1})
        quizzes = [
            {
                "_id": str(quiz["_id"]),
                "quiz": quiz["quiz"],
                "quizDescription": quiz.get("quizDescription", "No description available"),
                "quizSize": quiz.get("quizSize", 0)
            }
            for quiz in quizzes_cursor
        ]
        return jsonify({"quizzes": quizzes}), 200
    except Exception as e:
        return jsonify({"error": "Failed to fetch quizzes", "message": str(e)}), 500

@user.route('/user-home/start-quiz/<quiz_id>/', methods=['POST', 'GET'])
def user_start_quiz_splash(quiz_id):
    print(f"Recieved quiz_id: {quiz_id}")

    quiz_object_id = ObjectId(quiz_id)
    quiz = g.mongo_db.quizzes.find_one({"_id":quiz_object_id})

    print(f"Quiz: {quiz}")

    quiz_size = quiz["quizSize"]
    quiz_name = quiz["quiz"]
    quiz_description = quiz["quizDescription"]

    print(f"Quiz size: {quiz_size}")
    print(f"Quiz name: {quiz_name}")

    user_id = current_user.user_id

    token = serializer.dumps({"user_id":user_id, "quiz_id":quiz_id, "timestamp": time.time()})

    return render_template('user-start-quiz-splash.html', quiz_name=quiz_name, quiz_size=quiz_size, quiz_description=quiz_description, token=token)

@user.route('/api/initialize-quiz/<token>/')
def user_intialize_quiz(token):
    current_time = time.time()

    if token in QUIZ_CACHE:
        cached_quiz = QUIZ_CACHE[token]
        if current_time - cached_quiz["timestamp"] < LOCK_DURATION:
            print(f"Returning cached questions for token: {token}")
            return jsonify({"questions": cached_quiz["questions"], "quiz_name": cached_quiz["quiz_name"]})

    data = serializer.loads(token)
    if time.time() - data["timestamp"] > 3600:
        return jsonify({"error": "Token expired"}), 401
    
    user_id = data["user_id"]
    quiz_id = data["quiz_id"]

    quiz_object_id = ObjectId(quiz_id)
    quiz = g.mongo_db.quizzes.find_one({"_id": quiz_object_id})

    quiz_name = quiz["quiz"]
    groups = quiz["groups"]
    quiz_size = quiz["quizSize"]

    print(f"Quiz name: {quiz_name}")
    print(f"User: {user_id}")
    print(f"Groups: {groups}")
    print(f"Quiz size: {quiz_size}")

    all_questions = []

    for group_id in groups:
        group = g.mongo_db.groups.find_one({"_id": group_id})
        if group:
            print(f"Group: {group}")
            questions = group.get("questions", [])
            all_questions.extend(questions)
            print(f"Questions in group {group['name']}: {questions}")

    print(f"All questions: {all_questions}")

    if quiz_size > len(all_questions):
        return jsonify({"error": "Not enough questions available"}), 400

    selected_question_ids = []
    while len(selected_question_ids) < quiz_size:
        question_id = random.choice(all_questions)
        if question_id not in selected_question_ids:
            selected_question_ids.append(question_id)

    print(f"Initial selected question IDs: {selected_question_ids}")

    # Query for selected question details
    selected_questions = [
        g.mongo_db.questions.find_one({"_id": ObjectId(question_id)})
        for question_id in selected_question_ids
    ]

    # Backfill if needed
    selected_questions = [
        {
            "_id": str(q["_id"]),
            "questionText": q.get("questionText", ""),
            "questionType": str(q.get("questionType", "")),  # Ensure it's a string and not missing
            "answerOptions": q.get("answerOptions", []),
        }
        for q in selected_questions if q is not None  # Filter out None values
    ]

    print(f"Filtered valid questions: {selected_questions}")

    # If not enough valid questions, backfill
    remaining_question_ids = list(set(all_questions) - set(selected_question_ids))
    while len(selected_questions) < quiz_size and remaining_question_ids:
        backfill_id = random.choice(remaining_question_ids)
        backfill_question = g.mongo_db.questions.find_one({"_id": ObjectId(backfill_id)})
        if backfill_question:
            selected_questions.append(backfill_question)
            selected_question_ids.append(backfill_id)
            remaining_question_ids.remove(backfill_id)

    print(f"Final selected questions: {selected_questions}")

    # Cache selected questions and timestamp
    cached_questions = [
        {
            "_id": str(q["_id"]),
            "questionText": q["questionText"],
            "questionType": q["questionType"],  # Include questionType here
            "answerOptions": q["answerOptions"],
        }
        for q in selected_questions
    ]
    QUIZ_CACHE[token] = {
        "questions": cached_questions,
        "quiz_name": quiz_name,
        "timestamp": current_time,
    }
    print("Prepared selected questions for rendering:")
    for question in selected_questions:
        print("Question Text:", question.get("questionText"))
        print("Question Type:", question.get("questionType"))  # Check this field
        print("Answer Options:", question.get("answerOptions"))


    return jsonify({"questions": cached_questions, "quiz_name": quiz_name})

@user.route('/user-home/active-quiz/<token>/')
def user_active_quiz(token):

    response = user_intialize_quiz(token)
    quiz_data = response.get_json()

    if "error" in quiz_data:
        return quiz_data["error"]
    
    return render_template(
        'user-active-quiz.html',
        quiz_name=quiz_data["quiz_name"],
        selected_questions=quiz_data["questions"],
        token=token
    )

@user.route('/user-home/quiz-summary/')
def user_quiz_summary():
    submission_id = request.args.get("submission_id") or session.get("submission_id")
    if not submission_id:
        return jsonify({"error": "Submission ID is required"}), 400

    try:
        # Attempt to convert the submission_id to an ObjectId
        object_id = ObjectId(submission_id)
    except InvalidId:
        print(f"Invalid submission_id format: {submission_id}")
        return jsonify({"error": "Invalid submission ID format"}), 400

    # Retry logic to fetch the submission
    retries = 5
    for attempt in range(retries):
        submission = g.mongo_db.quiz_submission.find_one({"_id": object_id})
        print(f"User submission: {submission}")
        if submission:
            break
        print(f"Retry {attempt + 1}/{retries}: Submission not found. Retrying...")
        time.sleep(0.1)
    else:
        print(f"No quiz submission found for ID: {submission_id}")
        return jsonify({"error": "Quiz submission not found"}), 404
    
    # Fetch quiz details
    quiz = g.mongo_db.quizzes.find_one({"_id": ObjectId(submission["quiz_id"])})
    quiz_name = quiz["quiz"] if quiz else "Unknown Quiz"
    print(f"Quiz name: {quiz_name}")
    
    # Extract question_ids
    question_ids = submission.get("question_ids", [])
    print(f"Question IDs found in submission: {question_ids}")
    if not question_ids:
        print(f"No question IDs found in submission: {submission_id}")
        return jsonify({"error": "No questions found in submission"}), 400
    
    # Query questions from the database
    try:
        questions = list(g.mongo_db.questions.find({"_id": {"$in": question_ids}}))
        print(f"Retrieved questions for submission {submission_id}:")
        
        score = 0
        detailed_results = []

        for question in questions:
            question_id = str(question["_id"])

            # Adjust retrieval for `multipleAnswer` and other question types
            if question["questionType"] == "multipleAnswer":
                user_answer = submission["submission"].get(f"question_{question_id}[]", [])
                if not isinstance(user_answer, list):
                    user_answer = [user_answer] if user_answer else []
            else:
                user_answer = submission["submission"].get(f"question_{question_id}")

            # Retrieve correct answers
            if question["questionType"] == "multipleAnswer":
                correct_answers = [option["text"] for option in question["answerOptions"] if option.get("isCorrect")]
                is_correct = set(user_answer) == set(correct_answers)
            elif question["questionType"] == "openEnded":
                correct_answers = [option["text"] for option in question["answerOptions"]]
                is_correct = user_answer in correct_answers if user_answer else False
            else:
                correct_answers = [option["text"] for option in question["answerOptions"] if option.get("isCorrect")]
                is_correct = user_answer == correct_answers[0] if correct_answers else False

            # Increment score if correct
            if is_correct:
                score += 1

            # Add details to the results
            detailed_results.append({
                "questionText": question.get("questionText"),
                "userAnswer": user_answer,
                "correctAnswer": correct_answers,
                "isCorrect": is_correct
            })

            # Debugging output
            print(f"Question ID: {question_id}")
            print(f"User answer: {user_answer}")
            print(f"Correct answers: {correct_answers}")
            print(f"Is correct: {is_correct}")
            print(f"Score: {score}")

        users_score = f"{score}/{len(questions)}"
        print(f"User's score: {users_score}")
    except Exception as e:
        print(f"Error querying questions: {e}")
        return jsonify({"error": "Failed to retrieve questions", "message": str(e)})
    
    return render_template(
        'user-quiz-summary.html',
        submission=submission,
        questions=questions,
        detailed_results=detailed_results,
        users_score=users_score,
        quiz_name=quiz_name
    )

@user.route('/api/submit-quiz/<token>/', methods=['POST'])
def user_api_submit_quiz(token):
    # Validate the token
    try:
        data = serializer.loads(token)
        user_id = data["user_id"]
        quiz_id = data["quiz_id"]
        # print(f"User id:{user_id}")
        # print(f"Quiz id: {quiz_id}")
    except BadSignature:
        return jsonify({"error": "Invalid token"}), 401

    try:
        # Parse the submitted data
        submission = request.json
        # print(f"Submission data received: {submission}")

        # Extract question IDs
        question_ids = submission.get("question_ids", [])
        if not question_ids:
            return jsonify({"error": "No questions submitted"}), 400
        
        # print(f"Question ids: {question_ids}")

        # Ensure question_ids are valid ObjectId strings
        try:
            question_ids = [ObjectId(q_id) for q_id in question_ids]  # Transform question_ids to ObjectIds
        except Exception as e:
            return jsonify({"error": "Invalid question IDs", "message": str(e)}), 400

        # Save or process the submission
        try:
            submission_data = {
                "user_id": user_id,
                "quiz_id": quiz_id,
                "question_ids": question_ids,  # Save submitted question IDs
                "submission": submission,     # Save user responses
                "timestamp": datetime.utcnow()
            }
            result = g.mongo_db.quiz_submission.insert_one(submission_data)
            quiz_submission_id = str(result.inserted_id)
            print(f"Quiz submission saved with ID: {quiz_submission_id}")

            # Verify the document exists
            saved_submission = g.mongo_db.quiz_submission.find_one({"_id": result.inserted_id})
            if not saved_submission:
                print(f"Submission not available for ID: {quiz_submission_id}")
                return jsonify({"error": "Submission could not be verified"}), 500
            
            session["submission_id"] = quiz_submission_id

            return redirect(url_for('user.user_quiz_summary', submission_id=quiz_submission_id))
        
        except Exception as e:
            print(f"Database save error: {e}")
            return jsonify({"error": "Failed to save submission", "message": str(e)}), 500
        
    except Exception as e:
        print(f"Error processing submission: {e}")
        return jsonify({"error": "Invalid request format", "message": str(e)})

@user.route('/user-welcome/')
def user_welcome():
    return render_template('user-welcome.html')