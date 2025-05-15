from rest_framework import serializers
from .models import PaystackBank, UserBankAccount




class PaystackBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaystackBank
        fields = ['id', 'name', 'slug', 'code', 'longcode', 'country', 'currency', 'logo']
        read_only_fields = ['id', 'slug']





class UserBankAccountSerializer(serializers.ModelSerializer):
    bank = PaystackBankSerializer(read_only=True)
    bank_id = serializers.PrimaryKeyRelatedField(queryset=PaystackBank.objects.all(), source='bank', write_only=True)
    bank_name = serializers.CharField(source='bank.name', read_only=True)

    class Meta:
        model = UserBankAccount
        fields = ['id', 'user', 'bank', 'bank_id', 'bank_name', 'account_number', 'account_name', 'is_verified']
        read_only_fields = ['id', 'user', 'is_verified']