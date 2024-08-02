from django.urls import path
from rest_framework.authtoken import views
from .views import *

urlpatterns = [
    path("login/", views.obtain_auth_token),
    path("register/", RegisterUser.as_view()),
    path("logout/", Logout.as_view())
]