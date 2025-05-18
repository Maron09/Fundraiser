from rest_framework import serializers
from .models import PaystackBank, UserBankAccount
from paystack.api import Verification
import paystack
from django.conf import settings

paystack.api_key = settings.PAYSTACK_SECRET_KEY


class PaystackBankSerializer(serializers.ModelSerializer):
    class Meta:
        model = PaystackBank
        fields = ['id', 'name', 'slug', 'code', 'longcode', 'country', 'currency', 'logo']
        read_only_fields = ['id', 'slug']





class UserBankAccountSerializer(serializers.ModelSerializer):
    bank = PaystackBankSerializer(read_only=True)
    bank_name = serializers.CharField(write_only=True)
    bank_display = serializers.CharField(source='bank.name', read_only=True)

    class Meta:
        model = UserBankAccount
        fields = ['id', 'user', 'bank', 'bank_id', 'bank_name', 'bank_display', 'account_number', 'account_name', 'is_verified']
        read_only_fields = ['id', 'user', 'is_verified']
    
    
    def validate(self, attrs):
        account_number = attrs.get('account_number')
        bank_name_input = attrs.get('bank_name')
        if not bank_name_input:
            raise serializers.ValidationError({"bank_name": "This field is required."})
        
        normalized_bank_name = bank_name_input.lower().strip()
        try:
            bank = PaystackBank.objects.get(name__iexact=normalized_bank_name)
        except PaystackBank.DoesNotExist:
            raise serializers.ValidationError({
                "bank_name": f"Bank {bank_name_input} not found. Please enter a valid bank name."
            })
        
        bank_code = bank.code
        if not account_number.isdigit():
            raise serializers.ValidationError({
                "account_number": "Account number must be numeric."
            })
        if len(account_number) != 10:
            raise serializers.ValidationError({
                "account_number": "Account number must be 10 digits long."
            })
        
        response = Verification().resolve_account_number(
            account_number=account_number,
            bank_code=bank_code
        )
        
        if not response.status:
            raise serializers.ValidationError({
                "account_number": response.get("message", "could not verify account number.")
            })
        
        attrs["account_name"] = response.data.get("account_name")
        attrs["is_verified"] = True
        attrs["bank"] = bank
        del attrs["bank_name"]
        
        user = self.context['request'].user
        existing_accounts = UserBankAccount.objects.filter(user=user, bank=bank)
        if existing_accounts.filter(account_number=account_number).exists():
            raise serializers.ValidationError({
                "account_number": "This account number is already linked to your profile."
            })
        if existing_accounts.count() >= 3:
            raise serializers.ValidationError({
                "bank": "You can only link up to 3 accounts per bank."
            })
        return attrs
    
    def create(self, validated_data):
        validated_data["user"] = self.context['request'].user
        return super().create(validated_data)