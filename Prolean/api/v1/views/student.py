"""
Student Views for Prolean API
"""
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Q
from Prolean.models import (
    Profile, StudentProfile, Training, RecordedVideo, VideoProgress, Seance
)
from ..permissions import IsStudent, IsActiveStudent
from ..serializers.student import (
    StudentProfileSerializer,
    StudentDashboardSerializer,
    RecordedVideoSerializer,
    VideoProgressSerializer
)
from ..serializers.training import TrainingListSerializer
from ..serializers.auth import ProfileSerializer
from ..serializers.student_training import StudentTrainingDetailSerializer


class StudentProfileView(generics.RetrieveAPIView):
    """
    GET /api/v1/student/profile/
    Get current student's profile
    Requires authentication and STUDENT role
    """
    permission_classes = [IsActiveStudent]
    serializer_class = ProfileSerializer
    
    def get_object(self):
        return self.request.user.profile


class StudentDashboardView(APIView):
    """
    GET /api/v1/student/dashboard/
    Get comprehensive dashboard data for student
    Requires authentication and ACTIVE STUDENT status
    """
    permission_classes = [IsStudent]
    
    def get(self, request):
        profile = request.user.profile
        
        try:
            student_profile = profile.student_profile
        except StudentProfile.DoesNotExist:
            return Response({
                'error': 'Student profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get authorized formations
        authorized_formations = student_profile.authorized_formations.filter(is_active=True)
        
        # Get session
        session = student_profile.session
        
        # Get upcoming seances
        upcoming_seances = []
        if session:
            upcoming_seances = session.seances.filter(
                date__gte=timezone.now().date()
            ).order_by('date', 'time')[:5]
        
        # Get video progress summary
        video_progress_summary = {
            'total_videos': 0,
            'completed_videos': 0,
            'total_watch_time_seconds': 0
        }
        
        if authorized_formations.exists():
            # Get all videos for authorized formations
            total_videos = RecordedVideo.objects.filter(
                training__in=authorized_formations,
                is_active=True
            ).count()
            
            # Get progress
            progress_data = VideoProgress.objects.filter(
                student=profile
            ).aggregate(
                completed=Count('id', filter=Q(completed=True)),
                total_time=Sum('watched_seconds')
            )
            
            video_progress_summary = {
                'total_videos': total_videos,
                'completed_videos': progress_data['completed'] or 0,
                'total_watch_time_seconds': progress_data['total_time'] or 0
            }
        
        # Prepare dashboard data
        dashboard_data = {
            'profile': ProfileSerializer(profile).data,
            'student_profile': {
                'amount_paid': str(student_profile.amount_paid),
                'total_amount_due': str(student_profile.total_amount_due),
                'amount_remaining': str(student_profile.amount_remaining)
            },
            'authorized_formations': TrainingListSerializer(authorized_formations, many=True).data,
            'session': None,
            'upcoming_seances': [],
            'video_progress_summary': video_progress_summary
        }
        
        if session:
            from ..serializers.student import SessionSerializer, SeanceSerializer
            dashboard_data['session'] = SessionSerializer(session).data
            dashboard_data['upcoming_seances'] = SeanceSerializer(upcoming_seances, many=True).data
        
        return Response(dashboard_data, status=status.HTTP_200_OK)


class StudentFormationsView(generics.ListAPIView):
    """
    GET /api/v1/student/formations/
    Get student's authorized formations
    Requires authentication and ACTIVE STUDENT status
    """
    permission_classes = [IsStudent]
    serializer_class = TrainingListSerializer
    
    def get_queryset(self):
        try:
            student_profile = self.request.user.profile.student_profile
            return student_profile.authorized_formations.filter(is_active=True)
        except StudentProfile.DoesNotExist:
            return Training.objects.none()


class StudentSessionView(APIView):
    """
    GET /api/v1/student/session/
    Get student's assigned session details
    Requires authentication and ACTIVE STUDENT status
    """
    permission_classes = [IsStudent]
    
    def get(self, request):
        try:
            student_profile = request.user.profile.student_profile
            if not student_profile.session:
                return Response({
                    'message': 'No session assigned yet'
                }, status=status.HTTP_404_NOT_FOUND)
            
            from ..serializers.student import SessionSerializer
            return Response(
                SessionSerializer(student_profile.session).data,
                status=status.HTTP_200_OK
            )
        except StudentProfile.DoesNotExist:
            return Response({
                'error': 'Student profile not found'
            }, status=status.HTTP_404_NOT_FOUND)


class StudentVideosView(generics.ListAPIView):
    """
    GET /api/v1/student/videos/
    Get accessible video content for student
    Requires authentication and ACTIVE STUDENT status
    """
    permission_classes = [IsStudent]
    serializer_class = RecordedVideoSerializer
    
    def get_queryset(self):
        try:
            student_profile = self.request.user.profile.student_profile
            authorized_formations = student_profile.authorized_formations.filter(is_active=True)
            
            return RecordedVideo.objects.filter(
                training__in=authorized_formations,
                is_active=True
            ).order_by('training', 'created_at')
        except StudentProfile.DoesNotExist:
            return RecordedVideo.objects.none()
    
    def get_serializer_context(self):
        """Pass request to serializer for progress calculation"""
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class VideoProgressUpdateView(APIView):
    """
    POST /api/v1/student/videos/{video_id}/progress/
    Update video watch progress
    Requires authentication and ACTIVE STUDENT status
    """
    permission_classes = [IsStudent]
    
    def post(self, request, video_id):
        try:
            # Check if video exists and student has access
            student_profile = request.user.profile.student_profile
            authorized_formations = student_profile.authorized_formations.filter(is_active=True)
            
            video = RecordedVideo.objects.get(
                id=video_id,
                training__in=authorized_formations,
                is_active=True
            )
        except RecordedVideo.DoesNotExist:
            return Response({
                'error': 'Video not found or not authorized'
            }, status=status.HTTP_404_NOT_FOUND)
        except StudentProfile.DoesNotExist:
            return Response({
                'error': 'Student profile not found'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Get or create progress
        progress, created = VideoProgress.objects.get_or_create(
            student=request.user.profile,
            video=video
        )
        
        # Update progress
        watched_seconds = request.data.get('watched_seconds')
        completed = request.data.get('completed', False)
        
        if watched_seconds is not None:
            progress.watched_seconds = int(watched_seconds)
        
        if completed:
            progress.completed = True
        
        progress.save()
        
        return Response(
            VideoProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )
        return Response(
            VideoProgressSerializer(progress).data,
            status=status.HTTP_200_OK
        )


class StudentTrainingDetailView(generics.RetrieveAPIView):
    """
    GET /api/v1/student/formations/{id}/
    Get full details of a formation for a student (including videos)
    Requires authentication and ACTIVE STUDENT status
    """
    permission_classes = [IsStudent]
    serializer_class = StudentTrainingDetailSerializer
    lookup_field = 'id'
    
    def get_queryset(self):
        try:
            student_profile = self.request.user.profile.student_profile
            return student_profile.authorized_formations.filter(is_active=True)
        except StudentProfile.DoesNotExist:
            return Training.objects.none()
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context
