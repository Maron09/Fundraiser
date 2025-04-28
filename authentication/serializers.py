from rest_framework import serializers
from .models import User, PasswordResetToken
from django.contrib.auth import authenticate
from rest_framework.exceptions import AuthenticationFailed



class UserSerializer(serializers.ModelSerializer):
    """"
    Serializer for the User model.
    """
    
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    password2 = serializers.CharField(max_length=68, min_length=6, write_only=True)
    
    
    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password', 'password2']
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email already exists.")
        return email
    
    
    def create(self, validated_data):
        validated_data.pop('password2')
        return User.objects.create_user(**validated_data)


class RequestNewOTPSerializer(serializers.Serializer):
    """
    Serializer for requesting a new OTP.
    """
    
    email = serializers.EmailField(required=True)
    
    def validate_email(self, email):
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email does not exist.")
        return email



class LoginSerializer(serializers.ModelSerializer):
    """"
    Login serializer for the User model.
    """
    
    email = serializers.EmailField(max_length=255, min_length=6)
    password = serializers.CharField(max_length=68, min_length=6, write_only=True)
    full_name = serializers.CharField(read_only=True)
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    
    class Meta:
        model = User
        fields = ['email', 'password', 'full_name', 'access_token', 'refresh_token']
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        request = self.context.get("request")
        user = authenticate(request, email=email, password=password)
        if not user:
            raise AuthenticationFailed("Invalid credentials, try again.")
        if not user.is_active:
            raise AuthenticationFailed("Account disabled, contact admin or request a new OTP.")
        
        user_token = user.tokens()
        return {
            "email": email,
            "id": user.id,
            "full_name": user.get_full_name,
            "access_token": str(user_token.get("access")),
            "refresh_token": str(user_token.get("refresh")),
        }

class LogoutSerializer(serializers.Serializer):
    """"
    Logout serializer for the User model.
    """
    
    refresh = serializers.CharField()
    
    def validate(self, attrs):
        self.context["request"].auth.logout()
        return super().validate(attrs)


class PasswordResetRequestSerializer(serializers.Serializer):
    """"
    Password reset request serializer for the User model.
    """
    
    email = serializers.EmailField(required=True)
    
    def validate(self, data):
        email = data.get("email")
        if not User.objects.filter(email=email).exists():
            raise serializers.ValidationError("Email does not exist.")
        return data
    
    def create(self, validated_data):
        user = User.objects.get(email=validated_data["email"])
        PasswordResetToken.objects.create(user=user)
        return validated_data


class PasswordResetSerializer(serializers.Serializer):
    """""
    Reset password serializer for the User model.
    """
    
    token = serializers.UUIDField(required=True)
    new_password = serializers.CharField(max_length=68, min_length=6, write_only=True)  
    confirm_password = serializers.CharField(max_length=68, min_length=6, write_only=True)  
    
    def validate(self, data):
        new_password = data.get("new_password")
        confirm_password = data.get("confirm_password")
        
        try:
            reset_token = PasswordResetToken.objects.get(token=data["token"])
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError({"token": "Invalid token."})
        
        if reset_token.is_expired():
            raise serializers.ValidationError("Token has expired.")
        if new_password != confirm_password:
            raise serializers.ValidationError({"non_field_errors": ["Passwords do not match."]})
        
        data["user"] = reset_token.user
        return data
    
    def save(self):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        PasswordResetToken.objects.filter(user=user).delete()
