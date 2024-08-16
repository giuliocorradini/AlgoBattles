from rest_framework.test import APITestCase
from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token
import json

class TestUserLogging(APITestCase):
    """Test login and token generation"""

    def setUp(self):
        self.user = User.objects.create_user(username="test", password="a", email="test@algobattles.local")
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_login_valid_credentials(self):
        login_data = {
            "username": "test",
            "password": "a"
        }

        response = self.client.post("/api/auth/login/", login_data, format="json")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("token" in response.data)
        self.assertEqual(response.data.get("token"), self.token.key)

    def test_login_invalid_credentials(self):
        response = self.client.post("/api/auth/login/", {
            "username": "test",
            "password": "invalid"
        }, format="json")
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data, {
            "non_field_errors": [
                "Unable to log in with provided credentials."
            ]
        })

    def test_login_with_token(self):
        """Token is ignored"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        login_data = {
            "username": "test",
            "password": "a"
        }

        response = self.client.post("/api/auth/login/", login_data, format="json")

        print(response.data)

        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)
        self.assertEqual(self.token.key, response.data.get("token"))

    def test_login_with_token_invalid_credentials(self):
        """Token is ignored"""
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + self.token.key)

        login_data = {
            "username": "wronguser",
            "password": "a"
        }

        response = self.client.post("/api/auth/login/", login_data, format="json")

        print(response.data)

        self.assertNotEqual(response.status_code, 200)
        self.assertNotIn("token", response.data)


class TestUserSession(APITestCase):
    """Tests the entire session of a user, from registration, login to logout"""

    # We don't specify an explicit setUp here, but register_uesr takes the same place

    def register_user(self, username, password, email):
        userdata = {
            "username": username,
            "password": password,
            "email": email
        }

        return self.client.post("/api/auth/register/", userdata, format="json")
    
    def test_registration(self):
        response = self.register_user("test", "a", "test@algobattles.local")

        self.assertEqual(response.status_code, 201)
        self.assertIsNotNone(User.objects.get(username="test"))

    def test_login_and_logout(self):
        self.register_user("test", "a", "test@algobattles.local")

        login_data = {
            "username": "test",
            "password": "a"
        }

        response = self.client.post("/api/auth/login/", login_data, format="json")
        token = response.data.get("token")

        self.assertEqual(response.status_code, 200)
        self.assertTrue("token" in response.data)

        # Logout
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token)
        response = self.client.post("/api/auth/logout/")
        
        self.assertEqual(response.status_code, 205)
