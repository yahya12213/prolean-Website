"""
Training Serializers for Prolean API
"""
from rest_framework import serializers
from Prolean.models import Training, City


class CitySerializer(serializers.ModelSerializer):
    """Serializer for City model"""
    
    class Meta:
        model = City
        fields = ['id', 'name', 'region', 'phone', 'address', 'is_headquarters']


class TrainingListSerializer(serializers.ModelSerializer):
    """Serializer for Training list view (summary information)"""
    
    available_cities = serializers.SerializerMethodField()
    price = serializers.DecimalField(source='price_mad', max_digits=10, decimal_places=2, read_only=True)
    thumbnail_url = serializers.URLField(source='thumbnail', read_only=True)
    description = serializers.CharField(source='short_description', read_only=True)
    duration_hours = serializers.SerializerMethodField()
    module_count = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    
    class Meta:
        model = Training
        fields = [
            'id', 'title', 'slug', 'short_description', 'description', 
            'price_mad', 'price',
            'duration_days', 'duration_hours',
            'badge', 'is_featured', 'thumbnail', 'thumbnail_url',
            'available_cities', 'next_session', 'success_rate',
            'module_count', 'level'
        ]
    
    def get_available_cities(self, obj):
        """Get list of available city names"""
        return obj.get_available_cities()

    def get_duration_hours(self, obj):
        return obj.duration_days * 7  # Approximate 7 hours per day

    def get_module_count(self, obj):
        count = 0
        structure = obj.programme_structure or {}
        if 'theorique' in structure and 'modules' in structure['theorique']:
            count += len(structure['theorique']['modules'])
        if 'pratique' in structure and 'modules' in structure['pratique']:
            count += len(structure['pratique']['modules'])
        return count

    def get_level(self, obj):
        return 'intermediaire' # Default/Placeholder


class TrainingDetailSerializer(serializers.ModelSerializer):
    """Serializer for Training detail view (full information)"""
    
    available_cities = serializers.SerializerMethodField()
    gallery_images = serializers.SerializerMethodField()
    certificates = serializers.SerializerMethodField()
    features = serializers.SerializerMethodField()
    prerequisites = serializers.SerializerMethodField()
    faqs = serializers.SerializerMethodField()
    testimonials = serializers.SerializerMethodField()
    categories = serializers.SerializerMethodField()
    objectives_list = serializers.SerializerMethodField()
    programme_theorique_list = serializers.SerializerMethodField()
    programme_pratique_list = serializers.SerializerMethodField()
    
    # Frontend aliases
    price = serializers.DecimalField(source='price_mad', max_digits=10, decimal_places=2, read_only=True)
    thumbnail_url = serializers.URLField(source='thumbnail', read_only=True)
    duration_hours = serializers.SerializerMethodField()
    module_count = serializers.SerializerMethodField()
    level = serializers.SerializerMethodField()
    
    class Meta:
        model = Training
        fields = [
            # Basic info
            'id', 'title', 'slug', 'short_description', 'detailed_description',
            'objectives', 'objectives_list',
            
            # Pricing & Duration
            'price_mad', 'duration_days', 'max_students',
            
            # Programme
            'programme_structure', 'programme_theorique', 'programme_pratique',
            'programme_theorique_list', 'programme_pratique_list',
            
            # Stats & Badges
            'success_rate', 'badge', 'is_featured',
            
            # Images
            'thumbnail', 'programme_pdf_url', 'gallery_images', 'certificates',
            'license_recto_url', 'license_verso_url',
            
            # Cities
            'available_cities',
            
            # Statistics
            'stat_employment_rate', 'stat_student_satisfaction', 
            'stat_exam_success', 'stat_average_salary', 'stat_company_partnerships',
            
            # Features & Prerequisites
            'features', 'prerequisites',
            
            # FAQs & Testimonials
            'faqs', 'testimonials',
            
            # Categories
            'categories',
            
            # Schedule
            'next_session', 'schedule_json',
            
            # Metadata
            'created_at', 'view_count', 'inquiry_count', 'enrollment_count',
            
            # Frontend aliases
            'price', 'duration_hours', 'thumbnail_url', 'module_count', 'level'
        ]
    
    def get_available_cities(self, obj):
        return obj.get_available_cities()
    
    def get_gallery_images(self, obj):
        return obj.get_gallery_images(lang='fr')
    
    def get_certificates(self, obj):
        return obj.get_certificates(lang='fr')
    
    def get_features(self, obj):
        return obj.get_features(lang='fr')
    
    def get_prerequisites(self, obj):
        return obj.get_prerequisites(lang='fr')
    
    def get_faqs(self, obj):
        return obj.get_faqs(lang='fr')
    
    def get_testimonials(self, obj):
        return obj.get_testimonials(lang='fr')
    
    def get_categories(self, obj):
        return obj.get_categories()
    
    def get_objectives_list(self, obj):
        return obj.get_objectives_list(lang='fr')
    
    def get_programme_theorique_list(self, obj):
        return obj.get_programme_theorique_list(lang='fr')
    
    def get_programme_pratique_list(self, obj):
        return obj.get_programme_pratique_list(lang='fr')
        
    def get_duration_hours(self, obj):
        return obj.duration_days * 7

    def get_module_count(self, obj):
        count = 0
        structure = obj.programme_structure or {}
        if 'theorique' in structure and 'modules' in structure['theorique']:
            count += len(structure['theorique']['modules'])
        if 'pratique' in structure and 'modules' in structure['pratique']:
            count += len(structure['pratique']['modules'])
        return count

    def get_level(self, obj):
        return 'intermediaire'
