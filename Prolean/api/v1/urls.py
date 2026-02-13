"""
URL Configuration for Prolean API v1
"""
from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from .views.training import TrainingListView, TrainingDetailView, CityListView
from .views.auth import (
    StudentRegistrationView,
    StudentLoginView,
    StudentLogoutView,
    CustomTokenRefreshView
)
from .views.student import (
    StudentProfileView,
    StudentDashboardView,
    StudentFormationsView,
    StudentSessionView,
    StudentVideosView,
    StudentFormationsView,
    StudentSessionView,
    StudentVideosView,
    VideoProgressUpdateView,
    StudentTrainingDetailView
)
from .views.contact import ContactRequestView, PreInscriptionView

app_name = 'api_v1'

urlpatterns = [
    # ========== API Documentation ==========
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api_v1:schema'), name='docs'),
    
    # ========== Public Endpoints ==========
    # Formations
    path('formations/', TrainingListView.as_view(), name='formations-list'),
    path('formations/<slug:slug>/', TrainingDetailView.as_view(), name='formation-detail'),
    
    # Cities
    path('cities/', CityListView.as_view(), name='cities-list'),
    
    # Contact & Pre-inscription
    path('contact/', ContactRequestView.as_view(), name='contact'),
    path('pre-inscription/', PreInscriptionView.as_view(), name='pre-inscription'),
    
    # ========== Authentication Endpoints ==========
    path('auth/register/', StudentRegistrationView.as_view(), name='register'),
    path('auth/login/', StudentLoginView.as_view(), name='login'),
    path('auth/logout/', StudentLogoutView.as_view(), name='logout'),
    path('auth/refresh/', CustomTokenRefreshView.as_view(), name='token-refresh'),
    
    # ========== Student Endpoints (Authenticated) ==========
    path('student/profile/', StudentProfileView.as_view(), name='student-profile'),
    path('student/dashboard/', StudentDashboardView.as_view(), name='student-dashboard'),
    path('student/formations/', StudentFormationsView.as_view(), name='student-formations'),
    path('student/formations/<int:id>/', StudentTrainingDetailView.as_view(), name='student-formation-detail'),
    path('student/session/', StudentSessionView.as_view(), name='student-session'),
    path('student/videos/', StudentVideosView.as_view(), name='student-videos'),
    path('student/videos/<int:video_id>/progress/', VideoProgressUpdateView.as_view(), name='video-progress'),
]
