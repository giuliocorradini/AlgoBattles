from rest_framework import generics, pagination, views, status, viewsets, permissions
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from .. import serializers
from ..models import Puzzle, Category, PuzzleTest, Development, Attempt
from engine.tasks import test_chain
import logging
from django.db.models import Exists, OuterRef
from utils.permissions import IsBrowserAuthenticated, IsCORSOptions
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F, Value
from .permissions import IsPublisherPermission
from .serializers import PuzzleListSerializer, PuzzleSerializer, PuzzleEditSerializer

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'

class PublishedPuzzles(generics.ListAPIView):
    """Get published puzzles"""
    
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsCORSOptions | IsPublisherPermission, )
    pagination_class = StandardResultsSetPagination
    serializer_class = PuzzleListSerializer

    def get_queryset(self):
        return Puzzle.objects.filter(publisher=self.request.user)


class SearchPublisherPuzzleView(generics.ListAPIView):
    """Full text search on puzzle description and title for publisher."""
    serializer_class = PuzzleListSerializer
    pagination_class = StandardResultsSetPagination
    permission_classes = (IsCORSOptions | IsPublisherPermission, )

    def get_queryset(self):
        search_query = self.request.query_params.get('q', None)
        queryset = Puzzle.objects.filter(publisher=self.request.user)

        if search_query:
            query = SearchQuery(search_query)
            rank=SearchRank(F('search_vector'), query, normalization=Value(2))

            queryset = queryset.annotate(rank=rank).filter(rank__gt=0.001).order_by('-rank')
        else:
            queryset = Puzzle.objects.none()

        return queryset


class CreatePuzzleView(generics.CreateAPIView):
    """Publish a new puzzle"""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsCORSOptions | IsPublisherPermission, )
    serializer_class = PuzzleSerializer
    queryset = Puzzle.objects.all()


class PuzzleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Gets details about puzzle, allows update and destroy"""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsCORSOptions | IsPublisherPermission, )
    serializer_class = PuzzleEditSerializer

    def get_queryset(self):
        return Puzzle.objects.filter(publisher=self.request.user)
