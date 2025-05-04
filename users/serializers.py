import cloudinary.uploader
from rest_framework import serializers
from .models import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for the UserProfile model, handles Cloudinary uploads.
    """

    profile_picture = serializers.ImageField(required=False)

    class Meta:
        model = UserProfile
        fields = [
            "bio",
            "profile_picture",
            "address",
            "country",
            "state",
            "city",
        ]

    def update(self, instance, validated_data):
        profile_pic = validated_data.pop('profile_picture', None)

        # Handle Cloudinary upload if a new image is provided
        if profile_pic:
            upload_result = cloudinary.uploader.upload(profile_pic)
            instance.profile_picture = upload_result["secure_url"]

        # Update other fields normally
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance