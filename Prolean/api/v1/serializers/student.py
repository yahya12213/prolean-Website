"""
Student Serializers for Prolean API
"""
from rest_framework import serializers
from Prolean.models import (
    Profile, StudentProfile, Training, Session, Seance,
    RecordedVideo, VideoProgress, ProfessorProfile
)
from .auth import ProfileSerializer, UserSerializer
from .training import TrainingListSerializer


class StudentProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentProfile model"""
    
    profile = ProfileSerializer(read_only=True)
    authorized_formations = TrainingListSerializer(many=True, read_only=True)
    session_info = serializers.SerializerMethodField()
    amount_remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    
    class Meta:
        model = StudentProfile
        fields = [
            'id', 'profile', 'authorized_formations', 'session', 'session_info',
            'amount_paid', 'total_amount_due', 'amount_remaining'
        ]
        read_only_fields = ['id', 'amount_paid', 'total_amount_due']
    
    def get_session_info(self, obj):
        """Get session information if assigned"""
        if obj.session:
            return SessionSerializer(obj.session).data
        return None


class ProfessorSerializer(serializers.ModelSerializer):
    """Serializer for Professor information"""
    
    full_name = serializers.CharField(source='profile.full_name', read_only=True)
    
    class Meta:
        model = ProfessorProfile
        fields = ['id', 'full_name', 'specialization', 'bio']


class SeanceSerializer(serializers.ModelSerializer):
    """Serializer for Seance model"""
    
    class Meta:
        model = Seance
        fields = ['id', 'title', 'type', 'date', 'time', 'location']


class SessionSerializer(serializers.ModelSerializer):
    """Serializer for Session model"""
    
    formations = TrainingListSerializer(many=True, read_only=True)
    professor = ProfessorSerializer(read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    upcoming_seances = serializers.SerializerMethodField()
    
    # Frontend aliases
    name = serializers.SerializerMethodField()
    session_type = serializers.SerializerMethodField()
    formation_title = serializers.SerializerMethodField()
    
    class Meta:
        model = Session
        fields = [
            'id', 'formations', 'city', 'city_name', 'professor',
            'start_date', 'end_date', 'status', 'is_live', 
            'upcoming_seances', 'created_at',
            'name', 'session_type', 'formation_title'
        ]
    
    def get_upcoming_seances(self, obj):
        """Get upcoming seances for this session"""
        from django.utils import timezone
        upcoming = obj.seances.filter(date__gte=timezone.now().date()).order_by('date', 'time')[:5]
        return SeanceSerializer(upcoming, many=True).data

    def get_name(self, obj):
        return str(obj)

    def get_session_type(self, obj):
        return 'en_ligne' if obj.is_live else 'presentiel'

    def get_formation_title(self, obj):
        first = obj.formations.first()
        return first.title if first else ""


class VideoProgressSerializer(serializers.ModelSerializer):
    """Serializer for VideoProgress model"""
    
    class Meta:
        model = VideoProgress
        fields = ['id', 'video', 'watched_seconds', 'completed', 'last_watched_at']
        read_only_fields = ['id', 'last_watched_at']


class RecordedVideoSerializer(serializers.ModelSerializer):
    """Serializer for RecordedVideo model"""
    
    training_title = serializers.CharField(source='training.title', read_only=True)
    progress = serializers.SerializerMethodField()
    
    class Meta:
        model = RecordedVideo
        fields = [
            'id', 'training', 'training_title', 'title', 'description',
            'video_provider', 'video_id', 'duration_seconds', 'progress', 'created_at'
        ]
    
    def get_progress(self, obj):
        """Get video progress for current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                progress = VideoProgress.objects.get(
                    student=request.user.profile,
                    video=obj
                )
                return VideoProgressSerializer(progress).data
            except VideoProgress.DoesNotExist:
                return None
        return None


class StudentDashboardSerializer(serializers.Serializer):
    """Serializer for student dashboard data"""
    
    profile = ProfileSerializer()
    student_profile = StudentProfileSerializer()
    authorized_formations = TrainingListSerializer(many=True)
    session = SessionSerializer(allow_null=True)
    upcoming_seances = SeanceSerializer(many=True)
    video_progress_summary = serializers.DictField()
