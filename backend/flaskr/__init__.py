import os
from flask import Flask, request, abort, jsonify, Response
from json import dumps
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import random

from models import setup_db, Question, Category

QUESTIONS_PER_PAGE = 10


def paginated_questions(request, selection):
    page = request.args.get('page', 1, type=int)
    start = (page - 1) * QUESTIONS_PER_PAGE
    end = start + QUESTIONS_PER_PAGE

    questions = [question.format() for question in selection]
    current_questions = questions[start:end]

    return current_questions


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)

    '''
  @TODO: Set up CORS. Allow '*' for origins. Delete the sample route after completing the TODOs
  '''
    cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

    '''
  @TODO: Use the after_request decorator to set Access-Control-Allow
  '''
    @app.after_request
    def after_request(response):
        response.headers.add('Access-Control-Allow-Headers',
                             'Content-Type,Authorization,true')
        response.headers.add('Access-Control-Allow-Methods',
                             'GET,PUT,POST,DELETE,OPTIONS')
        return response

    '''
  @TODO:
  Create an endpoint to handle GET requests
  for all available categories.
  '''
    @app.route('/categories')
    def retrieve_categories():
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in categories]
        return jsonify({
            'success': True,
            'categories': formatted_categories,
            'no_of_categories': len(formatted_categories)
        })

    '''
  @TODO:
  Create an endpoint to handle GET requests for questions,
  including pagination (every 10 questions).
  This endpoint should return a list of questions,
  number of total questions, current category, categories.

  TEST: At this point, when you start the application
  you should see questions and categories generated,
  ten questions per page and pagination at the bottom of the screen for three pages.
  Clicking on the page numbers should update the questions.
  '''
    @app.route('/questions')
    def get_all_questions():
        selection = Question.query.all()
        current_content = paginated_questions(request, selection)
        categories = Category.query.order_by(Category.id).all()
        formatted_categories = [category.format() for category in categories]
        if len(current_content) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': current_content,
            'categories': formatted_categories,
            'total_questions': len(selection)
        })

    '''
  @TODO:
  Create an endpoint to DELETE question using a question ID.

  TEST: When you click the trash icon next to a question, the question will be removed.
  This removal will persist in the database and when you refresh the page.
  '''
    @app.route('/questions/<int:question_id>', methods=['DELETE'])
    def delete_questions(question_id):
        question = Question.query.filter(
            Question.id == question_id).one_or_none()
        try:
            question.delete()
            return jsonify({
                'success': True,
                'deleted': question_id,
            })

        except:
            if question is None:
                abort(404)
            else:
                abort(422)

    '''
  @TODO:
  Create an endpoint to POST a new question,
  which will require the question and answer text,
  category, and difficulty score.

  TEST: When you submit a question on the "Add" tab,
  the form will clear and the question will appear at the end of the last page
  of the questions list in the "List" tab.
  '''
    @app.route('/questions', methods=['POST'])
    def create_question():
        body = request.get_json()
        try:
            question = body.get('question', None)
            answer = body.get('answer', None)
            category = body.get('category', None)
            difficulty = body.get('difficulty', None)
        except:
            error_message = dumps({'success': False,
                                   'message': 'request body must match the parameters', 'parameters': [
                                       {
                                           'question': 'required',
                                           'type': 'string'
                                       },
                                       {
                                           'answer': 'required',
                                           'type': 'string'
                                       },
                                       {
                                           'category': 'required',
                                           'type': 'integer'
                                       },
                                       {
                                           'difficulty': 'required',
                                           'type': 'integer'
                                       },
                                   ]
                                   })
            abort(Response(error_message, 400))

        if question is None or answer is None or category is None or difficulty is None:
            abort(400)
        try:
            question = Question(
                question=question,
                answer=answer,
                category=category,
                difficulty=difficulty
            )
            question.insert()

            return jsonify({
                'success': True,
                'created': question.id
            })

        except:
            abort(422)
    '''
  @TODO:
  Create a POST endpoint to get questions based on a search term.
  It should return any questions for whom the search term
  is a substring of the question.

  TEST: Search by any phrase. The questions list will update to include
  only question that include that string within their question.
  Try using the word "title" to start.
  '''
    @app.route('/questions/search', methods=['POST'])
    def search_questions():
        search_term = request.get_json().get('searchTerm', None)
        questions = Question.query.filter(
            Question.question.ilike('%{}%'.format(search_term))).all()

        return jsonify({
            'questions': [question.format() for question in questions],
            'total_questions': len(questions)
        })

    '''
  @TODO:
  Create a GET endpoint to get questions based on category.

  TEST: In the "List" tab / main screen, clicking on one of the
  categories in the left column will cause only questions of that
  category to be shown.
  '''
    @app.route('/categories/<int:category_id>/questions')
    def question_in_category(category_id):
        questions = Question.query.filter(
            Question.category == category_id).all()

        if len(questions) == 0:
            abort(404)

        return jsonify({
            'success': True,
            'questions': [question.format() for question in questions],
            'total_questions': len(questions)
        })
    '''
  @TODO:
  Create a POST endpoint to get questions to play the quiz.
  This endpoint should take category and previous question parameters
  and return a random questions within the given category,
  if provided, and that is not one of the previous questions.

  TEST: In the "Play" tab, after a user selects "All" or a category,
  one question at a time is displayed, the user is allowed to answer
  and shown whether they were correct or not.
  '''
    @app.route('/quizzes', methods=['POST'])
    def get_quiz_question():
        body = request.get_json()
        previous_questions = body.get('previous_questions', [])
        quiz_category = body.get('quiz_category', None)

        if quiz_category is None or quiz_category['id'] == None or quiz_category['id'] == 0:
            questions = Question.query.all()
        elif quiz_category['id'] > 0:
            questions = Question.query.filter(
                Question.category == quiz_category['id']).all()
        else:
            abort(400)

        if len(questions) == 0:
            abort(404)

        filteredQuestions = [question.format() for question in questions]

        remainning_questions = [
            item for item in filteredQuestions if item not in previous_questions]

        if len(remainning_questions) < 1:
            return jsonify({
                'success': True,
                'question': 'All questions in the given category has been exhausted'
            })

        random_question = random.choice(remainning_questions)

        return jsonify({
            'success': True,
            'question': random_question
        })

    '''
  @TODO:
  Create error handlers for all expected errors
  including 404 and 422.
  '''
    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'message': 'Bad request',
            'status_code': 400
        }), 400

    @app.errorhandler(422)
    def unprocessable(error):
        return jsonify({
            'success': False,
            'message': 'Unprocessable',
            'status_code': 422
        }), 422

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'message': 'Resource Not Found',
            'status_code': 404
        }), 404

    return app
