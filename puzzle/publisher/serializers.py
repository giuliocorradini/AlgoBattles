from .. import models
from rest_framework import serializers

class PuzzleListSerializer(serializers.ModelSerializer):
    """Serializes a puzzle with categories as list, for list views"""
    categories = serializers.SerializerMethodField()

    class Meta:
        model = models.Puzzle
        fields = ("id", "title", "difficulty", "categories")

    def get_categories(self, obj):
        return list(obj.categories.values_list('name', flat=True))


class PuzzleSerializer(serializers.ModelSerializer):
    """Serializes a puzzle for creation and detail view. Categories are treated as a list field based
    on their unique name"""

    categories = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True
    )

    class Meta:
        model = models.Puzzle
        fields = [
            'id', 'title', 'difficulty', 'description', 
            'time_constraint', 'memory_constraint', 'categories',
            'visibility', 'publisher'
        ]
        read_only_fields = ['publisher']

    def create(self, validated_data):
        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            validated_data['publisher'] = request.user
        
        categories_data = validated_data.pop('categories', [])  # Remove categories from data dictionary
        puzzle = models.Puzzle.objects.create(**validated_data) # and create the actual object without

        # Categories are retrieved by their name from the database, or created
        for cat in categories_data:
            category, _ = models.Category.objects.get_or_create(name=cat)
            puzzle.categories.add(category)
        
        return puzzle

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['categories'] = [category.name for category in instance.categories.all()]
        return representation
