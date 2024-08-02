from . import models
from rest_framework import serializers


class PuzzleListSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    class Meta:
        model = models.Puzzle
        fields = ("id", "title", "difficulty", "categories")

    def get_categories(self, obj):
        return list(obj.categories.values_list('name', flat=True))


class PuzzleTestListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PuzzleTest
        fields = ("input", "output")


class PuzzleViewSerializer(serializers.ModelSerializer):
    categories = serializers.SerializerMethodField()

    def get_categories(self, obj):
        return list(obj.categories.values_list('name', flat=True))


    class Meta:
        model = models.Puzzle
        fields = "__all__"
