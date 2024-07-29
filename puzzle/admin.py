from django.contrib import admin

from .models import Puzzle, Category, PuzzleTest, PuzzleCategory

admin.site.register(Puzzle)
admin.site.register(Category)
admin.site.register(PuzzleCategory)
admin.site.register(PuzzleTest)