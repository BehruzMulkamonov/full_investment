from .models import SmartNote
from rest_framework import serializers
from full_data.models import MainData


class SmartNoteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartNote
        fields = ('id', 'main_data', 'text', 'name', 'custom_id', 'create_date_note')


class SmartNoteMainDataSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.CharField(source='main_data.enterprise_name', read_only=True)

    class Meta:
        model = MainData
        fields = ('id', 'enterprise_name')


class SmartNoteListRetrieveSerializer(serializers.ModelSerializer):
    main_data = SmartNoteMainDataSerializer()
    enterprise_name = serializers.SerializerMethodField()

    class Meta:
        model = SmartNote
        fields = ('id', 'enterprise_name', 'main_data', 'text', 'name', 'create_date_note', 'custom_id')

    def get_enterprise_name(self, object):
        main_data = object.main_data
        if main_data and main_data.enterprise_name:
            return main_data.enterprise_name
        else:
            return None


class SmartNoteUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = SmartNote
        fields = ('text', 'name', 'create_date_note', 'custom_id')


class CustomIdSerializer(serializers.Serializer):
    custom_id = serializers.CharField(max_length=30, allow_null=True, allow_blank=True)