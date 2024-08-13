from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient
import json

class TestCORSOnUserFullInformation(TestCase):
    """
    Test UserFullInformationView with IsBrowseAuthenticated, which rejects unauthenticated requests
    except for OPTIONS, which is used by the browser for CORS requests.
    """

    def setUp(self):
        self.user = User.objects.create(username="test", password="aaa", email="test@algobattles.com")
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def login(self):
        client = Client()
        response = client.post("/api/auth/login", {
            "username": "test",
            "password": "aaa"
        }, content_type="application/json")
        self.token = response.content.decode()

    def test_options_has_permission(self):
        client = Client()
        response = client.options("/api/user")

        self.assertEqual(response.status_code, 200)

    def test_get_unauth(self):
        client = Client()
        response = client.get("/api/user")

        self.assertEqual(response.status_code, 401)

    def test_get_auth(self):
        # Create a fake 
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {self.token}")

        response = client.get("/api/user")

        self.assertEqual(response.status, 200)
