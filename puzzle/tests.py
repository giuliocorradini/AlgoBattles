from django.test import TestCase
from rest_framework.test import APIClient
from .models import *

class AnonUserCapabilities(TestCase):
    """
    This class tests anonymous user capabilities. An anon user can view puzzles, open them in the editor
    but cannot submit any attempt.
    """

    def setUp(self):
        self.categories = ["greedy", "trees", "graphs", "recursion"]
        for cat in self.categories:
            Category.objects.create(name=cat)

        p = Puzzle.objects.create(
            title="Test puzzle 1",
            difficulty=Puzzle.DifficultyLevel.HARD,
            description="A description",
            time_constraint = 1,
            memory_constraint = 1,
        )
        p.categories.add(Category.objects.get(id=2))
        p.save()

        self.client = APIClient()
        

    # Public website section
    #   Puzzle categories, list, search by category and puzzle detail are part of
    #   the public section of the website. An anon user shoudl be able to retrieve this info.

    def test_categories(self):
        response = self.client.get("/api/category")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, self.categories)

    def test_puzzle_list(self):
        response = self.client.get("/api/puzzle")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("results" in response.data) # paginated
        self.assertIsInstance(response.data.get("results"), list)

    def test_puzzle_list_filter_by_category(self):
        response = self.client.get("/api/puzzle?category=trees")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("results" in response.data) # paginated
        self.assertIsInstance(response.data.get("results"), list)
        self.assertEqual(len(response.data.get("results")), 1)

    def test_puzzle_list_filter_by_difficulty(self):
        response = self.client.get("/api/puzzle?difficulty=E")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("results" in response.data) # paginated
        self.assertIsInstance(response.data.get("results"), list)
        self.assertEqual(len(response.data.get("results")), 0)

    def test_puzzle_details(self):
        response = self.client.get("/api/puzzle/1")
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue("description" in response.data)

    def test_puzzle_public_tests(self):
        response = self.client.get("/api/puzzle/1/test")
        
        self.assertEqual(response.status_code, 200)
    
    
    # Personal area
    #   includes personal completed, attempted puzzles and puzzle attempts. The capability of submitting
    #   an attempt is also subject to authorization.

    def test_get_attempts(self):
        response = self.client.get("/api/puzzle/1/attempt")

        self.assertEqual(response.status_code, 401)

    def test_submit_attempt(self):
        response = self.client.post("/api/puzzle/1/attempt")

        self.assertEqual(response.status_code, 401)

    def test_get_attempted_puzzles(self):
        response = self.client.get("/api/puzzle/attempted/")

        self.assertEqual(response.status_code, 401)
    
    def test_get_completed_puzzles(self):
        response = self.client.get("/api/puzzle/completed/")

        self.assertEqual(response.status_code, 401)
