from rest_framework import generics, pagination, views, status, authentication, viewsets
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from . import serializers
from .models import Puzzle, Category, PuzzleTest, Development, Attempt
from engine.tasks import build, test
import logging

logging.basicConfig(level=logging.INFO)

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

class AttemptsView(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = serializers.AttemptListSerializer

    def _corresponding_development(self, user, puzzle_id) -> Development:
        obj, created = Development.objects.get_or_create(user=user, puzzle_id=puzzle_id)
        return obj
    
    @action(detail=True, methods=["get"])
    def list_for_puzzle(self, request, pk=None):
        try:
            pk = int(pk)
        except ValueError:
            return Attempt.objects.none

        dev = self._corresponding_development(request.user, pk)
        res = Attempt.objects.filter(development__id=dev.id)
        serializer = self.get_serializer(res, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=["post"])
    def create_for_puzzle(self, request, pk):
        try:
            pk = int(pk)
        except ValueError:
            return Response({"reason": "Invalid puzzle key"}, status=status.HTTP_400_BAD_REQUEST)
        
        dev = self._corresponding_development(request.user, pk)

        # request.data is a base64 encoded JSON string representing the content of the editor

        a = Attempt.objects.create(development=dev, passed=False, results="")

        logging.info("Sending message to broker")
        logging.info(request.data)
        uid = str(a.pk)
        build.delay("c", request.data, uid)

        return Response(status=status.HTTP_201_CREATED)
