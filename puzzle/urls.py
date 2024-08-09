from django.urls import path, include
from . import views

urlpatterns = [
    path("category/", views.CategoryList.as_view(), name="category-list"),
    path("puzzle/", views.PuzzleList.as_view(), name="puzzle-list"),
    path("puzzle/<pk>/", views.PuzzleView.as_view(), name="puzzle"),
    path("puzzle/<pk>/test/", views.public_tests_for_puzzle, name="puzzle-tests-list"),
    path("puzzle/<pk>/attempt", views.AttemptsView.as_view({"get": "list_for_puzzle", "post": "create_for_puzzle"}), name="attempts-list"),
]
