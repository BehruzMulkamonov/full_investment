from rest_framework import serializers
from all_data.models import CadastralPhoto, InformativeData, ObjectPhoto, ProductPhoto
from django.core.files.base import ContentFile
import base64
import six
import uuid



class Base64ImageField(serializers.ImageField):
    """
    A Django REST framework field for handling image-uploads through raw post data.
    It uses base64 for encoding and decoding the contents of the file.

    Heavily based on
    https://github.com/tomchristie/django-rest-framework/pull/1268

    Updated for Django REST framework 3.
    """

    def to_internal_value(self, data):

        # Check if this is a base64 string
        if isinstance(data, six.string_types):
            # Check if the base64 string is in the "data:" format
            if 'data:' in data and ';base64,' in data:
                # Break out the header from the base64 content
                header, data = data.split(';base64,')

            # Try to decode the file. Return validation error if it fails.
            try:
                decoded_file = base64.b64decode(data)
            except TypeError:
                self.fail('invalid_image')

            # Generate file name:
            file_name = str(uuid.uuid4())[:12]  # 12 characters are more than enough.
            # Get the file name extension:
            file_extension = self.get_file_extension(file_name, decoded_file)

            complete_file_name = "%s.%s" % (file_name, file_extension,)

            data = ContentFile(decoded_file, name=complete_file_name)

        return super(Base64ImageField, self).to_internal_value(data)

    def get_file_extension(self, file_name, decoded_file):
        import imghdr

        extension = imghdr.what(file_name, decoded_file)
        extension = "jpg" if extension == "jpeg" else extension

        return extension


class CadastraInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CadastralPhoto
        fields = ('id', 'informative_data', 'image',)


class ProductPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductPhoto
        fields = ('id', 'informative_data', 'image',)

class ObjectPhotoSerializer(serializers.ModelSerializer):
    image = Base64ImageField(max_length=None, use_url=True)

    class Meta:
        model = ObjectPhoto
        fields = ('image',)
        
class InformativeDataSerializer(serializers.Serializer):
    product_info = serializers.CharField(max_length=30)
    project_capacity = serializers.CharField(max_length=30)
    formation_date = serializers.DateTimeField()
    total_area = serializers.DecimalField(max_digits=6, decimal_places=0)
    building_area = serializers.DecimalField(max_digits=6, decimal_places=0)
    tech_equipment = serializers.CharField(max_length=30)
    product_photo = Base64ImageField(max_length=None, use_url=True)
    cadastral_info = Base64ImageField(max_length=None, use_url=True)


class InformativeProDataSerializer(serializers.ModelSerializer):
    cadastral_info_list = CadastraInfoSerializer(many=True, read_only=True)
    product_photo_list = ProductPhotoSerializer(many=True, read_only=True)
    object_foto = ObjectPhotoSerializer(many=True, read_only=True)

    cadastral_info = serializers.ListField(
        child=serializers.ImageField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True
    )
    product_photo = serializers.ListField(
        child=serializers.ImageField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    object_photo = serializers.ListField(
        child=serializers.ImageField(max_length=1000, allow_empty_file=False, use_url=False),
        write_only=True
    )

    class Meta:
        model = InformativeData
        fields = ('product_info', 'project_capacity', 'total_area', 'formation_date',
                  'building_area', 'tech_equipment',
                  'cadastral_info', 'product_photo', 'object_photo',
                  'object_foto', 'cadastral_info_list', 'product_photo_list')

    def update(self, instance, validated_data):
        cadastral_info_data = validated_data.pop('cadastral_info', [])
        product_photo_data = validated_data.pop('product_photo', [])
        object_photos_data = validated_data.pop('object_photo', [])

        # Obyektni yangilash
        instance.product_info = validated_data.get('product_info', instance.product_info)
        instance.project_capacity = validated_data.get('project_capacity', instance.project_capacity)
        instance.total_area = validated_data.get('total_area', instance.total_area)
        instance.formation_date = validated_data.get('formation_date', instance.formation_date)
        instance.building_area = validated_data.get('building_area', instance.building_area)
        instance.tech_equipment = validated_data.get('tech_equipment', instance.tech_equipment)
        instance.save()

        instance.cadastral_info_list.all().delete()
        # CadastralPhoto obyektlarini yaratish va informative_data ni bog'lash
        [CadastralPhoto.objects.create(image=image_data, informative_data=instance) for
         image_data in cadastral_info_data]
        instance.product_photo_list.all().delete()

        [ProductPhoto.objects.create(image=photo_data, informative_data=instance) for
         photo_data in product_photo_data]
        instance.object_foto.all().delete()

        [ObjectPhoto.objects.create(image=obhect_data, informative_data=instance) for
         obhect_data in object_photos_data]

        return instance


class InformativeDataRetrieveSerializer(serializers.ModelSerializer):
    object_photos = ObjectPhotoSerializer(many=True)

    class Meta:
        model = InformativeData
        fields = (
            'id',
            'product_info',
            'project_capacity',
            'formation_date',
            'total_area',
            'building_area',
            'tech_equipment',
            'product_photo',
            'cadastral_info',
            'user',
            'object_photos'
        )


class InformativeProDataSerializerGet(serializers.ModelSerializer):
    cadastral_info_list = CadastraInfoSerializer(many=True, read_only=True)
    product_photo_list = ProductPhotoSerializer(many=True, read_only=True)
    object_foto = ObjectPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = InformativeData
        fields = ('product_info', 'project_capacity', 'total_area', 'formation_date',
                  'building_area', 'tech_equipment', 'object_foto',
                  'cadastral_info_list', 'product_photo_list')
        

class InformativeDataDraftSerializer(serializers.Serializer):
    product_info = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    project_capacity = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    formation_date = serializers.DateTimeField(allow_null=True, default=None)
    total_area = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
    building_area = serializers.DecimalField(max_digits=6, decimal_places=0, default=0)
    tech_equipment = serializers.CharField(max_length=30, allow_null=True, allow_blank=True, default='')
    product_photo = Base64ImageField(max_length=None, use_url=True, allow_null=True, default=None)
    cadastral_info = Base64ImageField(max_length=None, use_url=True, allow_null=True, default=None)



class InformativeDataGetSerializer(serializers.ModelSerializer):
    cadastral_info_list = CadastraInfoSerializer(many=True, read_only=True)
    product_photo_list = ProductPhotoSerializer(many=True, read_only=True)
    object_foto = ObjectPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = InformativeData
        fields = ('id', 'product_info', 'project_capacity', 'formation_date',
                  'total_area', 'building_area', 'tech_equipment',
                  'user', 'is_validated', 'object_foto', 'cadastral_info_list', 'product_photo_list')