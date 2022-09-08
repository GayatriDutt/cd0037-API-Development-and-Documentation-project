import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random


from models import setup_db, Question, Category

db = SQLAlchemy()
QUESTIONS_PER_PAGE = 10


def paginate(request, selection):
    page = request.args.get("page", 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_question = questions[start:end]

    return current_question


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    @app.after_request
    def after_request(response):
        response.headers.add(
            "Access-Control-Allow-Headers", "Content-Type,Authorization,true"
        )
        response.headers.add(
            "Access-Control-Allow-Methods", "GET,PUT,POST,DELETE,OPTIONS"
        )
        return response

    """
    @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
    """

    """
    @TODO: Use the after_request decorator to set Access-Control-Allow
    """

    """
    @TODO:
    Create an endpoint to handle GET requests
    for all available categories.
    """
    @app.route("/categories", methods=["GET"])
    def retrieve_categories():
        selection = Category.query.all()
        list = {}
        for i in selection:
            list[i.id] = i.type

        return jsonify(
            {
                "success": True,
                "categories": list
            }
        )

    """
    @TODO:
    Create an endpoint to handle GET requests for questions,
    including pagination (every 10 questions).
    This endpoint should return a list of questions,
    number of total questions, current category, categories.

    TEST: At this point, when you start the application
    you should see questions and categories generated,
    ten questions per page and pagination at the bottom of the screen for three pages.
    Clicking on the page numbers should update the questions.
    """
    @app.route("/questions", methods=["GET"])
    def retrieve_questions():
      selection = Question.query.all()
      current_questions = paginate(request, selection)

      categories = Category.query.all()
      list = {}
      for i in categories:
        list[i.id] = i.type
      return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(selection),
        "categories": list,
        "current_category": None})
    """
    @TODO:
    Create an endpoint to DELETE question using a question ID.

    TEST: When you click the trash icon next to a question, the question will be removed.
    This removal will persist in the database and when you refresh the page.
    """
    @app.route("/questions/<int:question_id>", methods=["DELETE"])
    def delete_questions(question_id):
        try:
            q = Question.query.filter(Question.id == question_id).one_or_none()

            if q is None:
                abort(404)

            q.delete()

            return jsonify(
                {
                    "success": True
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create an endpoint to POST a new question,
    which will require the question and answer text,
    category, and difficulty score.

    TEST: When you submit a question on the "Add" tab,
    the form will clear and the question will appear at the end of the last page
    of the questions list in the "List" tab.
    """
    @app.route("/questions", methods=["POST"])
    def create_question():
        body = request.get_json()

        new_question = body.get("question", None)
        new_difficulty = body.get("difficulty", None)
        new_answer = body.get("answer", None)
        new_category = body.get("category", None)

        try:
            q = Question(question=new_question, answer=new_answer,
                         difficulty=new_difficulty, category=new_category)
            q.insert()

            selection = Question.query.order_by(Question.id).all()
            current_questions = paginate(request, selection)

            return jsonify(
                {
                    "success": True,
                    "created": q.id,
                    "questions": current_questions,
                    "total_questions": len(Question.query.all()),
                }
            )

        except:
            abort(422)

    """
    @TODO:
    Create a POST endpoint to get questions based on a search term.
    It should return any questions for whom the search term
    is a substring of the question.

    TEST: Search by any phrase. The questions list will update to include
    only question that include that string within their question.
    Try using the word "title" to start.

    """
    @app.route("/questions/search", methods=["POST"])
    def search_for_question():
     body = request.get_json()
     search_term = body.get("searchTerm")

     try:

         selection = Question.query.filter(
             Question.question.ilike('%{}%'.format(search_term))).all()

         current_questions = paginate(request, selection)

         return jsonify({
        "success": True,
        "questions": current_questions,
        "total_questions": len(selection),
        "current_category": None
      })

     except:
        abort(422)

    """
    @TODO:
    Create a GET endpoint to get questions based on category.

    TEST: In the "List" tab / main screen, clicking on one of the
    categories in the left column will cause only questions of that
    category to be shown.
    """
    @app.route("/categories/<int:category_id>/questions", methods=["GET"])
    def get_questions_by_category(category_id):

        try:

            c = Category.query.get(category_id)
            
            questions = Question.query.filter_by(category=str(c)).all()
            list = []

            for question in questions:
                list.append(question.format())

            return jsonify(
                {
                    "success": True,
                    "questions": list,
                    "totalQuestions": len(list),
                    
                }
            )

        except Exception as ex:
            print("******", ex)
            abort(422)


    """
    @TODO:
    Create a POST endpoint to get questions to play the quiz.
    This endpoint should take category and previous question parameters
    and return a random questions within the given category,
    if provided, and that is not one of the previous questions.

    TEST: In the "Play" tab, after a user selects "All" or a category,
    one question at a time is displayed, the user is allowed to answer
    and shown whether they were correct or not.
    """

    @app.route("/quizzes", methods=["POST"])
    def play():

        body = request.get_json() 
        previous_questions = body.get("previous_questions")
        category = body.get("quiz_category") 
        questions = Question.query.filter_by(category=category.get("id")).all()
        print()

        next_questions = []

        for question in questions:
            if question.id not in previous_questions:
                next_questions.append(question)
                
                break

        return jsonify({"question": next_questions[0].format()})



        
    
    """
    @TODO:
    Create error handlers for all expected errors
    including 404 and 422.
    """


    @app.errorhandler(404)
    def not_found(error):
     return (
        jsonify({"success": False, "error": 404, "message": "not found"}),
        404,
    )

    @app.errorhandler(422)
    def unprocessable(error):
      return (
          jsonify({"success": False, "error": 422, "message": "unprocessable"}),
          422,
      )
    
    @app.errorhandler(405)
    def method_not_allowed(error):
      return (
          jsonify({"success": False, "error": 405, "message": "method not allowed"}),
          405,
      )
        
    return app

