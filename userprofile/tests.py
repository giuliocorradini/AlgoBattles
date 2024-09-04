from django.test import TestCase
from django.test import Client
from django.contrib.auth.models import User, Group
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient


class TestCORSOnUserFullInformation(TestCase):
    """
    Test UserFullInformationView with IsBrowseAuthenticated, which rejects unauthenticated requests
    except for OPTIONS, which is used by the browser for CORS requests.
    """

    def setUp(self):
        self.user = User.objects.create(username="test", password="aaa", email="test@algobattles.com")
        self.token, _ = Token.objects.get_or_create(user=self.user)

    def test_options_has_permission(self):
        client = Client()
        response = client.options("/api/user/")

        self.assertEqual(response.status_code, 200)

    def test_get_unauth(self):
        client = Client()
        response = client.get("/api/user/")

        self.assertEqual(response.status_code, 401)

    def test_get_auth(self):
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        response = client.get("/api/user/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("username"), "test")
        self.assertTrue("password" not in response.data)

    def test_publisher_role_on_non_publisher(self):
        """Tests if publisher role is communicated when doing an introspection.
        Testing against a non publisher, should yield false."""

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

        response = client.get("/api/user")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("username"), "test")
        self.assertTrue("is_publisher" in response.data)
        self.assertEqual(response.data.get("is_publisher"), False)
        
    def test_publisher_role_on_non_publisher(self):
        """Tests if publisher role is communicated when doing an introspection.
        Testing against a non publisher, should yield false."""

        pub = User.objects.create(username="publisher", password="aaa", email="publisher@algobattles.com")
        pubgroup, _ = Group.objects.get_or_create(name="Publishers")
        pub.groups.add(pubgroup)
        pubtoken, _ = Token.objects.get_or_create(user=pub)

        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION=f"Token {pubtoken.key}")

        response = client.get("/api/user/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data.get("username"), "publisher")
        self.assertTrue("is_publisher" in response.data)
        self.assertEqual(response.data.get("is_publisher"), True)
