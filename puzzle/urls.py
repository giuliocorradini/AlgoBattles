from django.urls import path, include
from . import views

urlpatterns = [
    path("category/", views.CategoryList.as_view(), name="category-list"),
    path("puzzle/", views.PuzzleList.as_view(), name="puzzle-list"),
]
