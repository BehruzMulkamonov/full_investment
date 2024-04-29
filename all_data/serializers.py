from rest_framework import serializers
from all_data.models import AllData, InvestorInfo
from financial_data.serializers import FinancialDataRetrieveCustomSerializer
from informative_data.serializers import InformativeProDataSerializerGet
from main_data.serializers import CoordinatesSerializer, MainDataRetrieveSerializer


class AllDataProSerializer(serializers.ModelSerializer):
    cat_name = serializers.SerializerMethodField()
    cat_id = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = ('id', 'main_data', 'informative_data', 'financial_data', 'date_created', 'cat_name', 'cat_id')

    def get_cat_name(self, obj):
        main_data = obj.main_data
        if main_data and main_data.category:
            return main_data.category.category
        return None

    def get_cat_id(self, obj):
        main_data = obj.main_data
        if main_data and main_data.category:
            return main_data.category.id
        return None
    

class AlldateCategorySerializer(serializers.ModelSerializer):
    main_name = serializers.SerializerMethodField()
    formation = serializers.SerializerMethodField()
    main_cat = serializers.SerializerMethodField()
    main_obj_photo = serializers.SerializerMethodField()
    main_area = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = ('id', 'main_name', 'formation', 'main_cat', 'main_obj_photo', 'main_area')  # `main_cat` ni qo'shdim

    def get_main_name(self, obj):
        return obj.main_data.enterprise_name

    def get_formation(self, obj):
        return obj.informative_data.formation_date

    def get_main_cat(self, obj):
        if obj.main_data.category:  # agar main_data da category mavjud bo'lsa
            return obj.main_data.category.category
        else:
            return None

    def get_main_area(self, obj):
        if obj.main_data.location:  # agar main_data da category mavjud bo'lsa
            return obj.main_data.location.location
        else:
            return None

    def get_main_obj_photo(self, obj):
        informative_model_photos = obj.informative_data.object_foto.all()
        image_urls = [photo.image.url for photo in informative_model_photos]
        return image_urls
    

class AllDataSerializer(serializers.ModelSerializer):
    main_data = MainDataRetrieveSerializer()
    informative_data = InformativeProDataSerializerGet()  # InformativeDataRetrieveSerializer() old version
    financial_data = FinancialDataRetrieveCustomSerializer()

    class Meta:
        model = AllData
        fields = (
            'id',
            'user',
            'main_data',
            'informative_data',
            'financial_data',
            'status',
            'date_created',
        )


class AllDataFilterSerializer(serializers.ModelSerializer):
    lat = serializers.SerializerMethodField()
    long = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = ('id', 'lat', 'long')

    def get_lat(self, object):
        return object.main_data.lat

    def get_long(self, object):
        return object.main_data.long
    

class ObjectIdAndCoordinatesSerializer(serializers.ModelSerializer):
    main_data = CoordinatesSerializer()

    class Meta:
        model = AllData
        fields = (
            'id',
            'main_data',
        )


class AllDataListSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = (
            'id',
            'enterprise_name',
            'status',
            'date_created',
        )

    def get_enterprise_name(self, object):
        return object.main_data.enterprise_name


class AllDataAllUsersListSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    product_info = serializers.SerializerMethodField()

    class Meta:
        model = AllData
        fields = (
            'id',
            'enterprise_name',
            'image',
            'product_info',
        )

    def get_enterprise_name(self, object):
        return object.main_data.enterprise_name

    def get_image(self, object):
        image = object.informative_data.object_photos.all().first()
        return_image = ''
        if image is not None:
            return_image = image.image.url
        return return_image

    def get_product_info(self, object):
        return object.informative_data.product_info


class InvestorInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorInfo
        fields = ('user_name', 'email', 'user_phone', 'message', 'file', 'all_data')


class InvestorInfoOwnSerializer(serializers.ModelSerializer):
    enterprise_name = serializers.SerializerMethodField()
    id_object = serializers.SerializerMethodField()

    class Meta:
        model = InvestorInfo
        fields = ('enterprise_name', 'id_object', 'message', 'date_created', 'status')

    def get_enterprise_name(self, object):
        return object.all_data.main_data.enterprise_name

    def get_id_object(self, object):
        return object.all_data.id


class ApproveRejectInvestorSerializer(serializers.Serializer):
    investor_id = serializers.IntegerField()
    all_data_id = serializers.IntegerField()
    is_approve = serializers.BooleanField()


class InvestorInfoGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = InvestorInfo
        fields = '__all__'


class InvestorInfoGetMinimumSerializer(serializers.ModelSerializer):
    message = serializers.SerializerMethodField()

    class Meta:
        model = InvestorInfo
        fields = ('user_name', 'id', 'date_created', 'message')

    def get_message(self, object):
        return object.message[:87] + '...'