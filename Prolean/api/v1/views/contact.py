"""
Contact and Pre-inscription Views for Prolean API
"""
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from rest_framework import serializers
from Prolean.models import ContactRequest, TrainingPreSubscription, Training


class ContactRequestSerializer(serializers.ModelSerializer):
    """Serializer for contact requests"""
    
    training_slug = serializers.SlugField(write_only=True, required=False)
    
    class Meta:
        model = ContactRequest
        fields = [
            'full_name', 'email', 'phone', 'city', 'country',
            'request_type', 'message', 'training_slug'
        ]
    
    def create(self, validated_data):
        training_slug = validated_data.pop('training_slug', None)
        
        # Get IP and user agent from request context
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            validated_data['session_id'] = request.session.session_key or ''
        
        # Link training if slug provided
        if training_slug:
            try:
                training = Training.objects.get(slug=training_slug, is_active=True)
                validated_data['training'] = training
                validated_data['training_title'] = training.title
            except Training.DoesNotExist:
                pass
        
        return super().create(validated_data)


class PreInscriptionSerializer(serializers.ModelSerializer):
    """Serializer for pre-inscription requests"""
    
    training_slug = serializers.SlugField(write_only=True)
    
    class Meta:
        model = TrainingPreSubscription
        fields = [
            'training_slug', 'full_name', 'email', 'phone', 'city',
            'payment_method'
        ]
    
    def validate_training_slug(self, value):
        """Validate training exists"""
        try:
            training = Training.objects.get(slug=value, is_active=True)
            return training
        except Training.DoesNotExist:
            raise serializers.ValidationError("Training not found")
    
    def create(self, validated_data):
        training = validated_data.pop('training_slug')
        
        # Get IP and user agent from request context
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
            validated_data['session_id'] = request.session.session_key or ''
        
        # Set training and prices
        validated_data['training'] = training
        validated_data['original_price_mad'] = training.price_mad
        validated_data['paid_price_mad'] = training.price_mad
        validated_data['currency_used'] = 'MAD'
        validated_data['payment_status'] = 'pending'
        
        return super().create(validated_data)


@method_decorator(ratelimit(key='ip', rate='5/h', method='POST'), name='dispatch')
class ContactRequestView(generics.CreateAPIView):
    """
    POST /api/v1/contact/
    Submit a contact request
    Public endpoint - no authentication required
    Rate limited: 5 requests per hour per IP
    """
    permission_classes = [AllowAny]
    serializer_class = ContactRequestSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        contact_request = serializer.save()
        
        return Response({
            'id': contact_request.id,
            'message': 'Your request has been submitted successfully. We will contact you soon.',
            'status': contact_request.status
        }, status=status.HTTP_201_CREATED)


@method_decorator(ratelimit(key='ip', rate='3/h', method='POST'), name='dispatch')
class PreInscriptionView(generics.CreateAPIView):
    """
    POST /api/v1/pre-inscription/
    Submit a pre-inscription request
    Public endpoint - no authentication required
    Rate limited: 3 requests per hour per IP
    """
    permission_classes = [AllowAny]
    serializer_class = PreInscriptionSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        pre_inscription = serializer.save()
        
        return Response({
            'transaction_id': str(pre_inscription.transaction_id),
            'message': 'Your pre-inscription has been submitted successfully. We will contact you to confirm payment details.',
            'payment_status': pre_inscription.payment_status,
            'amount': str(pre_inscription.paid_price_mad),
            'currency': pre_inscription.currency_used
        }, status=status.HTTP_201_CREATED)
