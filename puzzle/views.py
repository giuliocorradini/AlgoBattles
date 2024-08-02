from rest_framework import generics, pagination, views, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import serializers
from .models import Puzzle, Category, PuzzleTest

class CategoryList(views.APIView):
    def get(self, request):
        categories = Category.objects.values_list('name', flat=True)
        return Response(list(categories))


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class PuzzleList(generics.ListAPIView):
    serializer_class = serializers.PuzzleListSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        category = self.request.query_params.get("category", None)
        difficulty = self.request.query_params.get("difficulty", None)

        puzzles = Puzzle.objects.all()

        if category is not None:
            category = category.lower()
            puzzles = puzzles.filter(categories__name=category)

        if difficulty is not None:
            puzzles = puzzles.filter(difficulty=difficulty)
        
        return puzzles
    

class PuzzleView(generics.RetrieveAPIView):
    serializer_class = serializers.PuzzleViewSerializer
    
    def get_queryset(self):
        try:
            pk = int(self.kwargs['pk'])
        except ValueError:
            return Puzzle.objects.none

        return Puzzle.objects.filter(pk=pk)

@api_view(["GET"])
def public_tests_for_puzzle(request, pk):
    queryset = PuzzleTest.objects.all().filter(problem__id=pk, is_private=False)
    serializer = serializers.PuzzleTestListSerializer(queryset, many=True)

    return Response(serializer.data, status.HTTP_200_OK)
