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
from utils.permissions import IsBrowserAuthenticated
from django.contrib.postgres.search import SearchQuery, SearchRank
from django.db.models import F
from .permissions import IsPublisherPermission
from .serializers import PuzzleListSerializer, PuzzleSerializer

class StandardResultsSetPagination(pagination.PageNumberPagination):
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class PublishedPuzzles(generics.ListAPIView):
    """Get published puzzles"""
    
    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsBrowserAuthenticated, IsPublisherPermission)
    pagination_class = StandardResultsSetPagination
    serializer_class = PuzzleListSerializer

    def get_queryset(self):
        return Puzzle.objects.filter(publisher=self.request.user)


class CreatePuzzleView(generics.CreateAPIView):
    """Publish a new puzzle"""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsBrowserAuthenticated, IsPublisherPermission)
    serializer_class = PuzzleSerializer


class PuzzleDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Gets details about puzzle, allows update and destroy"""

    authentication_classes = (TokenAuthentication, )
    permission_classes = (IsBrowserAuthenticated, IsPublisherPermission)
    serializer_class = PuzzleSerializer
