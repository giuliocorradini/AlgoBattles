from rest_framework import generics, pagination, views, status, authentication
from rest_framework.decorators import api_view
from rest_framework.response import Response
from . import serializers
from .models import Puzzle, Category, PuzzleTest, Development, Attempt
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


class AttemptsForDevelopment(generics.ListAPIView):
    authentication_classes = [authentication.TokenAuthentication]
    serializer_class = serializers.AttemptListSerializer

    def _corresponding_development(self, user, puzzle_id) -> Development:
        obj, created = Development.objects.get_or_create(user=user, puzzle_id=puzzle_id)
        return obj
    
    def get_queryset(self):
        try:
            pk = int(self.kwargs['pk'])
        except ValueError:
            return Attempt.objects.none

        dev = self._corresponding_development(self.request.user, pk)
        return Attempt.objects.filter(development__id=dev.id)
    



#class PuzzleAttemptView(views.APIView):
#    """Handles attempts for a puzzle"""
#
#    authentication_classes = [authentication.TokenAuthentication]
#
#    def _corresponding_development(self, user, puzzle_id) -> Development:
#        return Development.objects.get_or_create(user=user, puzzle_id=puzzle_id)    # check consistency when passing invalid puzzle_id
#
#    def get(self, request):
#        """Inquiry the database for existing developments for a given problem"""
#        user = request.user
#
#        if user.is_anonymous:
#            logging.warn("Anonymous user. Beware of bugs")
#
#        try:
#            pk = int(self.kwargs['pk'])
#        except ValueError:
#            return Response({"reason": "Invalid puzzle ID format"}, status=status.HTTP_400_BAD_REQUEST)
#        
#        a = Development.objects.get()
#
#    def post(self, request):
#        user = request.user
#
#        if user.is_anonymous:
#            logging.warn("Anonymous user. Beware of bugs")
#
#        try:
#            pk = int(self.kwargs['pk'])
#        except ValueError:
#            return Response({"reason": "Invalid puzzle ID format"}, status=status.HTTP_400_BAD_REQUEST)
#        
#        d = Development.objects.create(user=user, puzzle_id=pk)
#        d.save()
#
#        return Response(status=status.HTTP_201_CREATED)
    