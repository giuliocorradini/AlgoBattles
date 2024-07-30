from django.urls import path, include
from . import views

urlpatterns = [
    path("category/", views.CategoryList.as_view(), name="category-list"),
    path("puzzle/", views.PuzzleList.as_view(), name="puzzle-list"),
    path("puzzle/<pk>/test", views.public_tests_for_puzzle, name="puzzle-tests-list"),
]
