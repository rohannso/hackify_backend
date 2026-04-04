from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import StudentProfile, FacultyProfile, OTP
import random
from django.conf import settings
from .utils import send_email_async

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'name', 'password', 'role']
    
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        otp_code = str(random.randint(100000, 999999))
        OTP.objects.create(user=user, code=otp_code)
        message = f'''
Hello {user.name},

Welcome to Hackify! 

Your email verification code is: {otp_code}

This code will expire in 10 minutes.

If you didn't request this, please ignore this email.

Best regards,
Hackify Team
    '''
    
        send_email_async(
        subject='Hackify - Email Verification Code',
        message=message,
        recipient_list=[user.email],
    )
    
        return user

class OTPVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    role = serializers.CharField()

class StudentProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentProfile
        fields = ['enrollment_no', 'department', 'year']

class FacultyProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = FacultyProfile
        fields = ['department', 'designation']

class UserDetailSerializer(serializers.ModelSerializer):
    student_profile = StudentProfileSerializer(read_only=True)
    faculty_profile = FacultyProfileSerializer(read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'role', 'is_verified', 'student_profile', 'faculty_profile']
class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp = serializers.CharField(max_length=6)
    new_password = serializers.CharField(min_length=6, write_only=True)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=6, write_only=True)
    new_password = serializers.CharField(min_length=6, write_only=True)
    confirm_password = serializers.CharField(min_length=6, write_only=True)
class ResendOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()


