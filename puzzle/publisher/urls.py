from django.urls import path
from .views import *

urlpatterns = [
    path("list", PublishedPuzzles.as_view(), name="publisher-get-all-puzzles"),
    path("create", CreatePuzzleView.as_view(), name="publisher-create-puzzle"),
    path("<int:pk>", PuzzleDetailView.as_view(), name="publisher-manage-detail-puzzle")
]
