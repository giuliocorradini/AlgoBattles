from . import models
from rest_framework import serializers


class PuzzleListSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = models.Puzzle
        fields = ("id", "title", "difficulty", "categories")

    def get_categories(self, obj):
        return list(obj.categories.values_list('name', flat=True))
