from rest_framework import serializers

from all_data.models import Currency, FinancialData


class FinancialDataSerializer(serializers.Serializer):
    export_share = serializers.DecimalField(max_digits=18, decimal_places=4)
    authorized_capital = serializers.DecimalField(max_digits=18, decimal_places=4)
    estimated_value = serializers.DecimalField(max_digits=18, decimal_places=4)
    investment_or_loan_amount = serializers.DecimalField(max_digits=18, decimal_places=4)
    investment_direction = serializers.CharField(max_length=30)
    major_shareholders = serializers.CharField(max_length=30)
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())

    def update(self, instance, validated_data):
        # Validated data bilan o'zgaruvchilarni yangilash
        instance.export_share = validated_data.get('export_share', instance.export_share)
        instance.authorized_capital = validated_data.get('authorized_capital', instance.authorized_capital)
        instance.estimated_value = validated_data.get('estimated_value', instance.estimated_value)
        instance.investment_or_loan_amount = validated_data.get('investment_or_loan_amount',
                                                                instance.investment_or_loan_amount)
        instance.investment_direction = validated_data.get('investment_direction', instance.investment_direction)
        instance.major_shareholders = validated_data.get('major_shareholders', instance.major_shareholders)
        instance.currency = validated_data.get('currency', instance.currency)

        # O'zgarishlarni saqlash
        instance.save()
        return instance
    

class FinancialDataDraftSerializer(serializers.Serializer):
    export_share = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    authorized_capital = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    estimated_value = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    investment_or_loan_amount = serializers.DecimalField(max_digits=18, decimal_places=4, default=0)
    investment_direction = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    major_shareholders = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    currency = serializers.PrimaryKeyRelatedField(queryset=Currency.objects.all())


    
class FinancialDataRetrieveCustomSerializer(serializers.ModelSerializer):
    currency = serializers.SerializerMethodField()

    class Meta:
        model = FinancialData
        fields = '__all__'

    def get_currency(self, object):
        return object.currency.code


class FinancialDataRetrieveSerializer(serializers.ModelSerializer):
    class Meta:
        model = FinancialData
        fields = '__all__'


class CurrencySerializer(serializers.ModelSerializer):
    class Meta:
        model = Currency
        fields = '__all__'