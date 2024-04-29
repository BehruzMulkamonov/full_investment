from rest_framework import serializers
from accounts.models import User  # accounts app dan User modelini import qiling
from all_data.models import AllData, Area, Category, MainData, Status
from all_data.serializers import AlldateCategorySerializer

class CategoryApiSerializer(serializers.ModelSerializer):
    main_data = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'category', 'main_data')
        read_only_fields = ('id',)

    def get_main_data(self, obj):
        main_data_objects = obj.main_data.all()

        serializer = MainDataSerializer(main_data_objects, many=True)

        return serializer.data


class CategoryApiProSerializer(serializers.ModelSerializer):
    alldata = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = ('id', 'category', 'alldata',)
        read_only_fields = ('id',)

    def get_alldata(self, obj):
        all_data_objects = AllData.objects.filter(main_data__category=obj, status=Status.APPROVED)
        serializer = AlldateCategorySerializer(all_data_objects, many=True)
        return serializer.data



class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        


class AreaAPISerializer(serializers.ModelSerializer):
    main_data = serializers.SerializerMethodField()

    class Meta:
        model = Area
        fields = ('id', 'location', 'main_data')
        read_only_fields = ('id',)

    def get_main_data(self, obj):
        main_data_objects = obj.main_data.all()

        serializer = MainDataSerializer(main_data_objects, many=True)

        return serializer.data



class AreaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = '__all__'


class MainDataAPISerializer(serializers.ModelSerializer):
    class Meta:
        model = MainData
        fields = ['enterprise_name', 'legal_form', 'location', 'lat', 'long', 'field_of_activity',
                  'infrastructure', 'project_staff', 'category', 'user']


class MainDataAPISerializer(serializers.ModelSerializer):
    location = serializers.PrimaryKeyRelatedField(queryset=Area.objects.all())
    category = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all())
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = MainData
        fields = ['enterprise_name', 'legal_form', 'location', 'lat', 'long', 'field_of_activity', 'infrastructure',
                  'project_staff', 'category', 'is_validated', 'user']


class MainDataSerializer(serializers.Serializer):
    enterprise_name = serializers.CharField(max_length=30)
    legal_form = serializers.CharField(max_length=30)
    location = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Area.objects.all())
    lat = serializers.DecimalField(max_digits=22, decimal_places=18)
    long = serializers.DecimalField(max_digits=22, decimal_places=18)
    field_of_activity = serializers.CharField(max_length=30)
    infrastructure = serializers.CharField(max_length=30)
    project_staff = serializers.DecimalField(max_digits=4, decimal_places=0)
    category = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Category.objects.all())


class MainDataRetrieveSerializer(serializers.ModelSerializer):
    category = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()

    class Meta:
        model = MainData
        fields = '__all__'

    def get_category(self, object):
        return object.category.category if object.category else None

    def get_location(self, object):
        return object.location.location if object.location else None
    

class MainDataDraftSerializer(serializers.Serializer):
    enterprise_name = serializers.CharField(max_length=256, allow_null=True, allow_blank=True, default='')
    legal_form = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    location = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Area.objects.all())
    lat = serializers.DecimalField(max_digits=22, decimal_places=18, default=0)
    long = serializers.DecimalField(max_digits=22, decimal_places=18, default=0)
    field_of_activity = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    infrastructure = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    project_staff = serializers.DecimalField(max_digits=4, decimal_places=0, default=0)
    category = serializers.PrimaryKeyRelatedField(allow_null=True, queryset=Category.objects.all())



class CoordinatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainData
        fields = ('lat', 'long',)


class LocationSerializer(serializers.Serializer):
    lat = serializers.DecimalField(max_digits=22, decimal_places=18)
    long = serializers.DecimalField(max_digits=22, decimal_places=18)