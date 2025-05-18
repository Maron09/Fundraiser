from rest_framework import serializers
from .models import Affiliate, AffiliateWallet, AffiliateTransaction, AffiliateWithdrawalRequest
from accounts.models import UserBankAccount
from .utils import generate_referral_code
from django.conf import settings
from .module import create_subaccount



class BecomeAffiliateSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Affiliate
        fields = ['user', 'referral_code', 'subaccount_code']
        read_only_fields = ['user', 'referral_code', 'subaccount_code']
    
    
    def validate(self, attrs):
        user = self.context['request'].user
        
        if Affiliate.objects.filter(user=user).exists():
            raise serializers.ValidationError("You are already an affiliate.")
        
        if not UserBankAccount.objects.filter(user=user).exists():
            raise serializers.ValidationError("You need to add a bank account before becoming an affiliate.")
        return attrs
    
    def create(self, validated_data):
        user = self.context["request"].user
        bank_account = UserBankAccount.objects.filter(user=user).first()

        subaccount_response = create_subaccount(
            business_name=f"{user.first_name} {user.last_name}",
            settlement_bank=bank_account.bank.code,
            account_number=bank_account.account_number,
        )
        if not subaccount_response.get('status'):
            raise serializers.ValidationError("Failed to create subaccount on Paystack.")

        subaccount_code = subaccount_response['data']['subaccount_code']

        affiliate = Affiliate.objects.create(
            user=user,
            referral_code=generate_referral_code(),
            subaccount_code=subaccount_code
        )
        return affiliate



class AffiliateWalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateWallet
        fields = ['balance']
        read_only_fields = ['affiliate', 'last_updated']


class AffiliateTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateTransaction
        fields = ['amount', 'transaction_type', 'timestamp']
        read_only_fields = ['wallet', 'timestamp']


class AffiliateWithdrawalRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = AffiliateWithdrawalRequest
        fields = ['amount']
        read_only_fields = ['affiliate', 'is_approved', 'created_at', 'processed_at']


    def validate_ammount(self, value):
        request = self.context['request']
        affiliate = getattr(request.user, 'affiliate', None)
        if not affiliate or not hasattr(affiliate, 'wallet'):
            raise serializers.ValidationError("You are not an affiliate or you do not have a wallet.")
        
        wallet = affiliate.wallet
        
        if value > wallet.balance:
            raise serializers.ValidationError("Insufficient balance in your wallet.")
        
        if value <= 0:
            raise serializers.ValidationError("Withdrawal amount must be greater than zero.")
        
        return value


