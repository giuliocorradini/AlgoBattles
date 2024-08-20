from rest_framework import generics, pagination, views, status, authentication, viewsets, permissions
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from . import serializers
from .models import Puzzle, Category, PuzzleTest, Development, Attempt
from engine.tasks import test_chain
import logging
from django.db.models import Exists, OuterRef
from utils.permissions import IsBrowserAuthenticated

MAX_FEATURED = 10   #TODO: move to settings.py

logging.basicConfig(level=logging.INFO)

class CategoryList(views.APIView):
    def get(self, request):
        featured = request.query_params.get("featured")
        if featured == "1":
            categories = Category.objects.filter(featured=True)

        else:
            categories = Category.objects.all()

        return Response(list(categories.values_list('name', flat=True)))

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
    

class FeaturedPuzzleView(views.APIView):
    def get(self, request, format=None):
        serializer_class = serializers.PuzzleListSerializer

        featured_cats = Category.objects.filter(featured=True)
        puzzles = [
            Puzzle.objects.filter(categories=fcat)[:MAX_FEATURED] for fcat in featured_cats
        ]

        data = [
            {
                "name": fcat.name,
                "puzzles": serializer_class(p, many=True).data
            } for fcat, p in zip(featured_cats, puzzles)
        ]

        return Response(data, status=status.HTTP_200_OK)

@api_view(["GET"])
def public_tests_for_puzzle(request, pk):
    queryset = PuzzleTest.objects.all().filter(puzzle__id=pk, is_private=False)
    serializer = serializers.PuzzleTestListSerializer(queryset, many=True)

    return Response(serializer.data, status.HTTP_200_OK)

class AttemptsView(viewsets.ModelViewSet):
    authentication_classes = [authentication.TokenAuthentication]
    permission_classes = (IsBrowserAuthenticated, )
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
            pk = int(pk)    #puzzle key
        except ValueError:
            return Response({"reason": "Invalid puzzle key"}, status=status.HTTP_400_BAD_REQUEST)
        
        dev = self._corresponding_development(request.user, pk)

        a = Attempt.objects.create(development=dev, passed=False, results="")
        uid = str(a.pk)

        priv_tests = PuzzleTest.objects.filter(puzzle__id=pk, is_private=True)

        tests = [(i, t.input, t.output) for i, t in enumerate(priv_tests)]

        print(tests)

        task_result = test_chain(request.data.get("language"), request.data.get("source"), uid, tests)
        a.task_id = task_result.id
        a.save()

        return Response({"id": a.pk}, status=status.HTTP_201_CREATED)
    

class PollingAttemptResultView(generics.RetrieveAPIView):
    """Gets the result of a build-test chain with polling"""
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (IsBrowserAuthenticated,)
    serializer_class = serializers.AttemptListSerializer

    def get_object(self):
        try:
            tid = int(self.kwargs['tid'])
        except ValueError:
            return None

        return Attempt.objects.get(
            pk=tid,
            development__user=self.request.user
        )


class AttemptedPuzzleView(generics.ListAPIView):
    """Returns a list of attempted puzzle for the authenticated user."""

    serializer_class = serializers.PuzzleListSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Puzzle.objects.filter(
            Exists(
                Development.objects.filter(
                    puzzle=OuterRef('pk'),
                    user=self.request.user
                )
            )
        )
    

class CompletedPuzzleView(generics.ListAPIView):
    """Returns a list of completed puzzle for the authenticated user."""

    serializer_class = serializers.PuzzleListSerializer
    authentication_classes = (authentication.TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        return Puzzle.objects.filter(
            Exists(
                Development.objects.filter(
                    puzzle=OuterRef('pk'),
                    user=self.request.user,
                    completed=True
                )
            )
        )
