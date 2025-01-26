from flask import Blueprint, render_template, url_for, jsonify, request, abort, g
from .models import db, User, Role
from .utils import bcrypt
from datetime import datetime
from flask_login import current_user, login_required
from . import csrf, limiter
from .decorators import role_required
from bson.objectid import ObjectId

admin = Blueprint('admin', __name__)

@admin.route('/admin-home/')
@login_required
@role_required('admin')
def admin_home():
    return render_template('admin-home.html')

@admin.route('/admin-welcome/')
@login_required
@role_required('admin')
def admin_welcome():
    return render_template('admin-welcome.html')

@admin.route('/admin-home/users/')
@login_required
@role_required('admin')
def admin_users():
    users = User.query.all()
    return render_template('admin-users.html', user=users)

@admin.route('/admin-home/admin-quizzes')
@login_required
@role_required('admin')
def admin_quizzes():
    return render_template('admin-quizzes.html')

@admin.route('/admin-home/create-group/', methods=['POST'])
@csrf.exempt  # Ensure CSRF is checked
@limiter.limit("5 per minute")  # Prevent abuse
@login_required
@role_required('admin')
def admin_create_group():
    """
    Creates a group in the database.
    """
    try:
        # Parse the JSON payload
        data = request.get_json()

        # Extract group name
        group_name = data.get('name', '').strip()
        if not group_name:
            print("Group name is missing.")
            return jsonify({'error': 'Group name is required.'}), 400

        # Prepare the document
        new_group = {
            "_id": ObjectId(),
            "name": group_name,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "questions": []
        }
        print("New group:", new_group)

        # Insert into MongoDB (example with PyMongo)
        groups_collection = g.mongo_db["groups"]
        groups_collection.insert_one(new_group)
        print("Group successfully added.")

        return jsonify({'success': 'Group created successfully.', 'groupId': str(new_group["_id"])}), 201
    except Exception as e:
        print("Error:", e)
        return jsonify({'error': str(e)}), 500

@admin.route('/admin-home/create-question/', methods=['POST'])
@csrf.exempt
@limiter.limit("5 per minute")
@login_required
@role_required('admin')
def admin_create_question():
    """
    Creates a new question and assigns it to a group in MongoDB.
    """
    try:
        # Parse the JSON payload
        data = request.get_json()

        # Validate required fields
        question_type = data.get("questionType", "").strip()
        question_text = data.get("questionText", "").strip()
        question_media = data.get("questionMedia", "").strip()
        group_id = data.get("groupId", "").strip()
        answer_options = data.get("answerOptions", [])

        if not question_type or not question_text or not group_id:
            return jsonify({'error': 'Question type, question text, and group ID are required.'}), 400

        # Handle specific question types
        if question_type == "trueFalse":
            correct_answer = data.get("correctAnswer", "").strip()
            if correct_answer not in ["True", "False"]:
                return jsonify({'error': 'Valid correct answer (True/False) is required.'}), 400

            answer_options = [
                {"text": "True", "isCorrect": correct_answer == "True"},
                {"text": "False", "isCorrect": correct_answer == "False"}
            ]

        elif question_type == "openEnded":
            correct_answer = data.get("correctAnswer", "").strip()
            if not correct_answer:
                return jsonify({'error': 'Correct answer is required for open-ended questions.'}), 400

            answer_options = [{"text": correct_answer}]

        elif question_type in ["multipleChoice", "multipleAnswer"]:
            if not isinstance(answer_options, list) or not answer_options:
                return jsonify({'error': 'Answer options are required for this question type.'}), 400

        # Prepare the question document
        question_doc = {
            "_id": ObjectId(),
            "questionType": question_type,
            "questionText": question_text,
            "questionMedia": question_media,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user.user_id,
            "updatedBy": current_user.user_id,
            "answerOptions": answer_options
        }

        # Save to MongoDB questions collection
        questions_collection = g.mongo_db["questions"]
        questions_collection.insert_one(question_doc)
        question_id = str(question_doc["_id"])

        # Update the selected group with the new question
        groups_collection = g.mongo_db["groups"]
        update_result = groups_collection.update_one(
            {"_id": ObjectId(group_id)},
            {"$push": {"questions": question_id}}
        )

        if update_result.matched_count == 0:
            return jsonify({'error': 'Group not found.'}), 404

        return jsonify({'success': 'Question created and assigned to group successfully.', 'questionId': question_id}), 201
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({'error': 'An error occurred while creating the question.'}), 500

@admin.route('/admin-home/get-groups/', methods=['GET'])
@login_required
@role_required('admin')
def get_groups():
    """
    Fetch all group names and IDs from MongoDB.
    """
    try:
        groups_collection = g.mongo_db["groups"]
        groups = list(groups_collection.find({}, {"_id": 1, "name": 1}))
        return jsonify([{"_id": str(group["_id"]), "name": group["name"]} for group in groups]), 200
    except Exception as e:
        print(f"Error fetching groups: {e}")
        return jsonify({'error': 'Failed to fetch groups.'}), 500

@admin.route('/admin-home/create-quiz/', methods=['POST'])
@csrf.exempt  # Ensure CSRF is checked
@limiter.limit("5 per minute")  # Prevent abuse
@login_required
@role_required('admin')
def admin_create_quiz():
    """
    Creates a new quiz and saves it to MongoDB.
    """
    try:
        # Parse the JSON payload
        data = request.get_json()

        # Validate required fields
        quiz_name = data.get("quiz", "").strip()
        quiz_description = data.get("quizDescription", "").strip()
        quiz_size = data.get("quizSize", 0)
        group_ids = data.get("groups", [])

        if not quiz_name or not quiz_description or not group_ids or quiz_size < 1:
            return jsonify({'error': 'All fields are required and quiz size must be at least 1.'}), 400

        # Prepare the quiz document
        quiz_doc = {
            "_id": ObjectId(),
            "quiz": quiz_name,
            "quizDescription": quiz_description,
            "createdAt": datetime.utcnow(),
            "updatedAt": datetime.utcnow(),
            "createdBy": current_user.user_id,
            "updatedBy": current_user.user_id,
            "quizSize": quiz_size,
            "groups": [ObjectId(group_id) for group_id in group_ids]
        }

        # Save to MongoDB quizzes collection
        quizzes_collection = g.mongo_db["quizzes"]
        quizzes_collection.insert_one(quiz_doc)

        return jsonify({'success': 'Quiz created successfully.', 'quizId': str(quiz_doc["_id"])}), 201
    except Exception as e:
        print(f"Error creating quiz: {e}")
        return jsonify({'error': 'An error occurred while creating the quiz.'}), 500

@admin.route('/admin-home/create-user/submit/', methods=['POST'])
@csrf.exempt  # Ensure CSRF is checked
@limiter.limit("5 per minute")  # Prevent abuse
@login_required
@role_required('admin')
def admin_create_user():
    # Ensure current user is admin
    if current_user.role.role_name != 'admin':
        abort(403, description="You are not authorized to perform this action.")

    # Parse form inputs
    email = request.form.get('email', '').strip()
    password = request.form.get('password', '').strip()
    role = request.form.get('role', '').strip()
    first_name = request.form.get('first_name', '').strip()
    last_name = request.form.get('last_name', '').strip()

    # Validate required fields
    if not email or not password or not role:
        return jsonify({'error': 'Email, password, and role are required.'}), 400

    if role not in ['admin', 'user']:
        return jsonify({'error': 'Invalid role provided.'}), 400

    # Check if the email already exists
    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists.'}), 400

    # Hash the password
    hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

    # Fetch the role ID using the role name
    user_role = Role.query.filter_by(role_name=role).first()
    if not user_role:
        return jsonify({'error': 'Role not found in database.'}), 500

    # Create the new user
    new_user = User(
        email=email,
        password=hashed_password,
        role_id=user_role.role_id,  # Use the role ID for foreign key
        first_name=first_name,
        last_name=last_name,
        created_by=current_user.user_id,  # Reference the admin's user_id
        first_login=True,
        password_last_changed=datetime.utcnow(),
        is_active=True,  # Default new users to active
    )

    # Save to database
    db.session.add(new_user)
    db.session.commit()

    return jsonify({'success': 'User created successfully.'}), 201

