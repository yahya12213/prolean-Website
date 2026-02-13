"""
Authentication Serializers for Prolean API
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.core.validators import RegexValidator
from Prolean.models import Profile, StudentProfile, City


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        read_only_fields = ['id']


class ProfileSerializer(serializers.ModelSerializer):
    """Serializer for Profile model"""
    
    user = UserSerializer(read_only=True)
    city_name = serializers.CharField(source='city.name', read_only=True)
    
    class Meta:
        model = Profile
        fields = [
            'id', 'user', 'role', 'full_name', 'cin_or_passport',
            'phone_number', 'city', 'city_name', 'status', 
            'email_verified', 'profile_picture', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'role', 'status', 'email_verified', 'created_at', 'updated_at']


class StudentRegistrationSerializer(serializers.Serializer):
    """Serializer for student registration"""
    
    username = serializers.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[\w.@+-]+$',
                message='Username can only contain letters, numbers, and @/./+/-/_ characters.'
            )
        ]
    )
    email = serializers.EmailField()
    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={'input_type': 'password'}
    )
    full_name = serializers.CharField(max_length=200)
    phone_number = serializers.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^\+?[0-9]{10,15}$',
                message='Phone number must be 10-15 digits, optionally starting with +'
            )
        ]
    )
    city_id = serializers.IntegerField()
    cin_or_passport = serializers.CharField(max_length=50, required=False, allow_blank=True)
    
    def validate_username(self, value):
        """Check if username already exists"""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        return value
    
    def validate_email(self, value):
        """Check if email already exists"""
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        return value
    
    def validate_phone_number(self, value):
        """Check if phone number already exists"""
        if Profile.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("A user with this phone number already exists.")
        return value
    
    def validate_city_id(self, value):
        """Check if city exists"""
        if not City.objects.filter(id=value, is_active=True).exists():
            raise serializers.ValidationError("Invalid city ID.")
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        validate_password(value)
        return value
    
    def create(self, validated_data):
        """Create user and profile"""
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Update profile (created automatically by signal)
        profile = user.profile
        profile.full_name = validated_data['full_name']
        profile.phone_number = validated_data['phone_number']
        profile.city_id = validated_data['city_id']
        profile.role = 'STUDENT'
        profile.status = 'PENDING'  # Requires admin activation
        
        if validated_data.get('cin_or_passport'):
            profile.cin_or_passport = validated_data['cin_or_passport']
        
        profile.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for login"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True, style={'input_type': 'password'})


class LoginResponseSerializer(serializers.Serializer):
    """Serializer for login response"""
    
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = UserSerializer()
    profile = ProfileSerializer()
