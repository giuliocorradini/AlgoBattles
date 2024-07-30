from rest_framework import generics, pagination, views
from rest_framework.response import Response
from . import models, serializers

class CategoryList(views.APIView):
    def get(self, request):
        categories = models.Category.objects.values_list('name', flat=True)
        return Response(list(categories))


class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class PuzzleList(generics.ListAPIView):
    queryset = models.Puzzle.objects.all()
    serializer_class = serializers.PuzzleListSerializer
    pagination_class = StandardResultsSetPagination
