import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy

from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_path = 'postgresql://tunde@localhost:5432/trivia_test'
        self.new_question = {
            'question': 'What is name of the third planet in our solar system',
            'answer': 'Earth',
            'difficulty': 3,
            'category': 1,
        }
        self.bad_question = {
            'answer': 'Jupiter',
            'difficulty': 2,
            'category': 1,
        }
        self.searchTerm = {
            'searchTerm': 'planet',
        }
        self.all_category_game = {
            'previous_questions': [],
            'quiz_category': {'type': 'click', 'id': 0}
        }

        self.specific_category_game = {
            'previous_questions': [],
            'quiz_category': {'type': 'Sports', 'id': 6}
        }
        setup_db(self.app, self.database_path)

        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()

    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for
    successful operation and for expected errors.
    """

    def test_get_categories(self):
        response = self.client().get('/categories')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['categories']))

    def test_get_questions(self):
        response = self.client().get('/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['success'])
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['categories']))

    def test_delete_question(self):
        initial_res = self.client().post('/questions', json=self.new_question)
        question_to_delete = json.loads(initial_res.data)['created']

        res = self.client().delete('/questions/{}'.format(question_to_delete))
        data = json.loads(res.data)

        question = Question.query.filter(
            Question.id == question_to_delete
        ).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertTrue(data['success'])
        self.assertEqual(data['deleted'], question_to_delete)
        self.assertEqual(question, None)

    def test_404_if_question_does_not_exist(self):
        res = self.client().delete('/questions/1000')
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertFalse(data['success'])
        self.assertEqual(data['message'], 'Resource Not Found')

    def test_create_question(self):
        response = self.client().post('/questions', json=self.new_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(data['created'])
        self.assertTrue(data['success'])

    def test_400_bad_request_for_new_question(self):
        response = self.client().post('/questions', json=self.bad_question)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 400)
        self.assertFalse(data['success'])

    def test_search_questions(self):
        response = self.client().post(
            '/questions/search', json=self.searchTerm
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['total_questions'])

    def test_get_questions_by_category(self):
        response = self.client().get('/categories/2/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['questions']) > 0)
        self.assertTrue(data['total_questions'])

    def test_get_questions_by_non_existing_category(self):
        response = self.client().get('/categories/2000/questions')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 404)
        self.assertFalse(data['success'])

    def test_play_quiz_all_categories(self):
        response = self.client().post('/quizzes', json=self.all_category_game)
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['question']))

    def test_play_quiz_specific_category(self):
        response = self.client().post(
            '/quizzes', json=self.specific_category_game
        )
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(data['question']))


# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
