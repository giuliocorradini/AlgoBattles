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

class PuzzleTestSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.PuzzleTest
        fields = ['input', 'output', 'is_private']

class PuzzleSerializer(serializers.ModelSerializer):
    """Serializes a puzzle for creation and detail view. Categories are treated as a list field based
    on their unique name"""

    tests = PuzzleTestSerializer(many=True, write_only=True)
    categories = serializers.ListField(
        child=serializers.CharField(max_length=100),
        write_only=True
    )

    class Meta:
        model = models.Puzzle
        fields = (
            'id', 'title', 'difficulty', 'description', 'time_constraint', 'memory_constraint', 'categories', 'visibility', 'publisher', 'tests'
        )
        read_only_fields = ('id', 'publisher')

    def create(self, validated_data):
        request = self.context.get('request')

        if request and hasattr(request, 'user'):
            validated_data['publisher'] = request.user
        
        categories_data = validated_data.pop('categories', [])  # Remove categories from data dictionary
        tests_data = validated_data.pop('tests')

        puzzle = models.Puzzle.objects.create(**validated_data) # and create the actual object without

        # Categories are retrieved by their name from the database, or created
        for cat in categories_data:
            category, _ = models.Category.objects.get_or_create(name=cat)
            puzzle.categories.add(category)
        
        for test in tests_data:
            models.PuzzleTest.objects.create(puzzle=puzzle, **test)        

        return puzzle

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation['categories'] = [category.name for category in instance.categories.all()]
        return representation


class PuzzleEditSerializer(PuzzleSerializer):
    def update(self, instance, validated_data):
        # Update categories by their name
        category_names = validated_data.pop('categories', None)

        if category_names is not None:
            instance.categories.clear()
            
            for cat in category_names:
                category, _ = models.Category.objects.get_or_create(name=cat)
                instance.categories.add(category)
        
        tests_data = validated_data.pop('tests', None)
        if tests_data:
            models.PuzzleTest.objects.filter(puzzle=instance).delete()
            for test in tests_data:
                models.PuzzleTest.objects.create(puzzle=instance, **test)

        # Update other fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance    
