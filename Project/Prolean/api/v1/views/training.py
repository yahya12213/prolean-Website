"""
Training Views for Prolean API
"""
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from Prolean.models import Training, City
from ..serializers.training import (
    TrainingListSerializer,
    TrainingDetailSerializer,
    CitySerializer
)


class TrainingListView(generics.ListAPIView):
    """
    GET /api/v1/formations/
    List all active formations
    Public endpoint - no authentication required
    """
    permission_classes = [AllowAny]
    serializer_class = TrainingListSerializer
    queryset = Training.objects.filter(is_active=True).order_by('-is_featured', '-created_at')
    
    def get_queryset(self):
        """Filter by category if provided"""
        queryset = super().get_queryset()
        
        # Filter by category
        category = self.request.query_params.get('category', None)
        if category:
            category_field = f'category_{category}'
            if hasattr(Training, category_field):
                queryset = queryset.filter(**{category_field: True})
        
        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            city_field = f'available_{city.lower()}'
            if hasattr(Training, city_field):
                queryset = queryset.filter(**{city_field: True})
        
        # Filter by featured
        featured = self.request.query_params.get('featured', None)
        if featured and featured.lower() == 'true':
            queryset = queryset.filter(is_featured=True)
        
        return queryset


class TrainingDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/formations/{slug}/
    Get formation details by slug
    Public endpoint - no authentication required
    """
    permission_classes = [AllowAny]
    serializer_class = TrainingDetailSerializer
    queryset = Training.objects.filter(is_active=True)
    lookup_field = 'slug'
    
    def retrieve(self, request, *args, **kwargs):
        """Increment view count when retrieving"""
        instance = self.get_object()
        instance.increment_view_count()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class CityListView(generics.ListAPIView):
    """
    GET /api/v1/cities/
    List all active cities
    Public endpoint - no authentication required
    """
    permission_classes = [AllowAny]
    serializer_class = CitySerializer
    queryset = City.objects.filter(is_active=True).order_by('name')
