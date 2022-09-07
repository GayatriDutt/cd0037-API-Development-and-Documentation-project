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
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)

     
        self.new_question = {
        "question": 'Example Question?',
        "answer": 'Example Answer',
        "category": 1,
        "difficulty": 1
        }
        self.question_to_delete = {
            "question": "deleteme",
            "answer": "pleasedeleteme",
            "category": 2,
            "difficulty": 4,
        }
        
        self.search_test = {"searchTerm": "title"}
        
        self.search_test_no_results = {"searchTerm": "no results"}

        self.new_quiz = {
        "previous_questions": [],
        "quiz_category": {"type": 'Science' , "id": 3}
        }
        self.error_quiz = {
        "previous_questions": [],
        "quiz_category": {}
        }

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
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_retrieve_categories(self):
        res = self.client().get("/categories")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["categories"])

    def test_retrieve_questions(self):
        res = self.client().get("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertTrue(len(data["questions"]))
        self.assertTrue(data["total_questions"])
        self.assertTrue(len(data["categories"]))
    
    def test_405_question_error(self):
        res = self.client().patch("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")

    def test_delete_questions(self):
        res = self.client().post("/questions", json=self.question_to_delete)
        data = json.loads(res.data)
        id=data["id"]

        delete=self.client().delete("/questions/{}".format(id))
        self.assertEqual(delete.status_code, 200)
        self.assertEqual(delete["success"], True)
    
   
    
    def test_create_question(self):
        res = self.client().post("/questions", json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
    
    def test_405_if_question_creation_fails(self):
        res = self.client().patch("/questions")
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 405)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "method not allowed")
    
    def test_search_for_question(self):
        res = self.client().post("/questions/search", json=self.search_test)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        

    def test_search_for_question_failure(self):
        res = self.client().post("/questions/search", json=self.search_test_no_results)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(len(data["questions"]), 0)

    
    def test_get_questions_by_category(self):
        res = self.client().get("category/30/questions")
        data = json.loads(res.data)
       
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["questions"])
        self.assertEqual(data["total_questions"], True)
        self.assertTrue(data["current_category"]) 

    def test_play(self):
        res = self.client().post("/quizzes", json=self.new_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data["success"], True)
        self.assertTrue(data["question"]) 
    
    def test_play_error(self):
        res = self.client().post("/quizzes", json=self.error_quiz)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data["success"], False)
        self.assertEqual(data["message"], "unprocessable")
    


    
    




# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()