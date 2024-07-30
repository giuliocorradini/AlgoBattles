from django.contrib import admin

from .models import Puzzle, Category, PuzzleTest

admin.site.register(Puzzle)
admin.site.register(Category)
admin.site.register(PuzzleTest)