from rest_framework import serializers
from .models import Campaign, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['name', 'slug']



class CampaignSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), write_only=True)
    owner = serializers.StringRelatedField(read_only=True)
    image = serializers.ImageField(required=True)
    remaining_days = serializers.SerializerMethodField()
    # Uncomment when Donation model is implemented
    
    total_raised = serializers.SerializerMethodField()
    progress = serializers.SerializerMethodField()

    class Meta:
        model = Campaign
        fields = [
            'owner', 'category', 'category_id', 'title', 'slug', 'description',
            'goal', 'image', 'start_date', 'end_date', 'is_active',
            'created_at', 'updated_at', 'remaining_days', 'total_raised',
            'progress', 'is_expired'
        ]
    
    def create(self, validated_data):
        validated_data['owner'] = self.context['request'].user
        validated_data['category'] = validated_data.pop('category_id')
        return super().create(validated_data)

    def get_remaining_days(self, obj):
        return obj.remaining_days

    # Uncomment when Donation model is implemented
    
    def get_total_raised(self, obj):
        return obj.total_raised

    def get_progress(self, obj):
        return round(obj.progress, 2)

    def get_is_expired(self, obj):
        return obj.is_expired

    def get_category_id(self, obj):
        return obj.category.id if obj.category else None