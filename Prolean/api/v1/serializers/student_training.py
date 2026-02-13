from rest_framework import serializers
from Prolean.models import Training, RecordedVideo, VideoProgress

class StudentFeaturedVideoSerializer(serializers.ModelSerializer):
    """Serializer for videos in the student details view"""
    is_completed = serializers.SerializerMethodField()
    duration_minutes = serializers.SerializerMethodField()
    
    class Meta:
        model = RecordedVideo
        fields = ['id', 'title', 'description', 'video_provider', 'video_id', 'duration_seconds', 'duration_minutes', 'is_completed']

    def get_is_completed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            try:
                # Optimized: This should ideally be prefetched
                return VideoProgress.objects.filter(
                    student=request.user.profile,
                    video=obj,
                    completed=True
                ).exists()
            except:
                return False
        return False

    def get_duration_minutes(self, obj):
        return obj.duration_seconds // 60

class StudentTrainingDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for full training details for a student.
    Constructs a 'virtual' module structure since we don't have real modules.
    """
    modules = serializers.SerializerMethodField()
    summary = serializers.SerializerMethodField()
    thumbnail_url = serializers.URLField(source='thumbnail', read_only=True)
    level = serializers.SerializerMethodField()
    duration_hours = serializers.SerializerMethodField()
    passing_score_percentage = serializers.SerializerMethodField()
    
    class Meta:
        model = Training
        fields = [
            'id', 'title', 'short_description', 'description', 'thumbnail_url',
            'modules', 'summary', 'level', 'duration_hours', 'passing_score_percentage'
        ]

    def get_summary(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return None
            
        videos = RecordedVideo.objects.filter(training=obj, is_active=True)
        total_videos = videos.count()
        
        from Prolean.models import VideoProgress
        from django.db.models import Count, Q
        
        progress = VideoProgress.objects.filter(
            student=request.user.profile,
            video__training=obj
        ).aggregate(
            completed=Count('id', filter=Q(completed=True))
        )
        
        completed_videos = progress['completed'] or 0
        overall_progress = (completed_videos / total_videos * 100) if total_videos > 0 else 0
        
        return {
            'total_videos': total_videos,
            'completed_videos': completed_videos,
            'total_tests': 0, # Backend doesn't support tests yet
            'passed_tests': 0,
            'overall_progress': round(overall_progress, 1)
        }

    def get_modules(self, obj):
        # Fetch all active videos for this training
        videos = RecordedVideo.objects.filter(training=obj, is_active=True).order_by('created_at')
        video_serializer = StudentFeaturedVideoSerializer(videos, many=True, context=self.context)
        
        # Create a single default module containing all content
        # In a real system with Module models, we would iterate over them.
        return [{
            'id': f'default-{obj.id}',
            'title': 'Contenu de la formation',
            'description': 'Tous les chapitres et vidéos',
            'module_type': 'video', 
            'duration_minutes': sum(v.duration_seconds for v in videos) // 60,
            'videos': video_serializer.data,
            'tests': [] # We can add tests here later if needed
        }]

    def get_level(self, obj):
        return 'intermediaire'
        
    def get_duration_hours(self, obj):
        return obj.duration_days * 7

    def get_passing_score_percentage(self, obj):
        return 70 # Default Value
