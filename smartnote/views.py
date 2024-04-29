from rest_framework import generics, status, permissions, views, mixins, viewsets
from rest_framework.response import Response
from all_data.models import Status
from .serializer import SmartNoteCreateSerializer, SmartNote,SmartNoteListRetrieveSerializer,SmartNoteMainDataSerializer, SmartNoteUpdateSerializer, CustomIdSerializer
from django.db.models import Q
from uuid import uuid4
from rest_framework.response import Response
from rest_framework import status


class SmartNoteCreateView(generics.CreateAPIView):
    serializer_class = SmartNoteCreateSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Serializer orqali ma'lumotlar olish
        custom_id = serializer.validated_data.get('custom_id')
        
        # Agar foydalanuvchi tizimga kirgan bo'lsa
        if self.request.user.is_authenticated:
            instance = SmartNote(user=self.request.user)
            
            # Agar custom_id kiritilgan bo'lsa
            if custom_id != '':
                # user__isnull=True sharti ostida bo'lgan SmartNote obyektlarini olish
                notes = SmartNote.objects.filter(
                    custom_id=serializer.validated_data['custom_id'],
                    user__isnull=True
                )
                # Agar shunday obyekt mavjud bo'lsa, foydalanuvchiga bog'lash
                if notes.exists():
                    notes.update(user=self.request.user)
        else:
            # Agar foydalanuvchi tizimga kirmagan bo'lsa
            # custom_id kiritilmagan bo'lsa, unga uni avtomatik tuzatish
            if custom_id == '':
                custom_id = str(uuid4())[-12:]
            instance = SmartNote(custom_id=custom_id)
        
        # Barcha ma'lumotlarni SmartNote obyektiga o'rnatish
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        
        # custom_id bo'sh bo'lmasa uni o'rnatish
        if custom_id != '':
            instance.custom_id = custom_id
        
        # SmartNote obyektini saqlash
        instance.save()
        
        # Kiritilgan obyektning ma'lumotlarini chiqarish uchun serializer ishlatiladi
        data_for_return = SmartNoteCreateSerializer(instance)
        
        # Ushbu ma'lumotni chiqarish uchun muvaffaqiyatli headerlar
        headers = self.get_success_headers(serializer.data)
        
        # Muvaffaqiyatli HTTP 201 Created javobi qaytariladi
        return Response(data_for_return.data, status=status.HTTP_201_CREATED, headers=headers)
    


class SmartNoteListView(generics.ListAPIView):
    queryset = SmartNote.objects.all()  # Ma'lumotlar ro'yxatini olish uchun queryset
    serializer_class = SmartNoteListRetrieveSerializer  # Serializer uchun qo'llaniladigan klass
    permission_classes = (permissions.AllowAny,)  # Foydalanuvchiga ruxsat berilgan ishlar

    def post(self, request, *args, **kwargs):
        # Serializer obyektini yaratish va ma'lumotlarni tekshirish
        serializer = CustomIdSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        # Agar foydalanuvchi tizimga kirgan bo'lsa
        if self.request.user.is_authenticated:
            # Foydalanuvchi to'g'risidagi ma'lumotlarni olish
            datas = SmartNote.objects.filter(user=self.request.user).select_related('main_data')
        else:
            # Agar foydalanuvchi tizimga kirmagan bo'lsa
            custom_id = serializer.validated_data.get('custom_id')
            if custom_id != '':
                # Custom ID boyicha ma'lumotlarni olish
                datas = SmartNote.objects.filter(custom_id=custom_id).select_related('main_data')
            else:
                datas = None

        # Serializer bilan ma'lumotlarni seriylash
        serializer_info = SmartNoteListRetrieveSerializer(datas, many=True)
        
        # Ma'lumotlarni JSON formatiga o'zgartirish va qaytarish
        return Response(serializer_info.data, status=status.HTTP_200_OK)
    



class SmartNoteRetrieveView(generics.CreateAPIView):
    serializer_class = SmartNoteListRetrieveSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        # Serializer obyektini yaratish va ma'lumotlarni tekshirish
        serializer = CustomIdSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        
        # lookup_url_kwarg ni aniqlash
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        # Filterni tayyorlash
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        queryset = Q(status=Status.APPROVED)
        
        # Agar foydalanuvchi tizimga kirgan bo'lsa
        if self.request.user.is_authenticated:
            queryset = Q(user=self.request.user)
        else:
            # Agar foydalanuvchi tizimga kirmagan bo'lsa
            custom_id = serializer.validated_data.get('custom_id')
            if custom_id != '':
                queryset = Q(custom_id=custom_id)
            else:
                queryset = Q(user__id=-985)  # user__id=-985 da SmartNote obyekti mavjud emas

        # Ma'lumotlarni olish
        datas = SmartNote.objects.filter(queryset, **filter_kwargs).select_related('main_data').first()

        # Ma'lumotlarni seriylash
        serializer_info = SmartNoteListRetrieveSerializer(datas)

        # Ma'lumotlarni JSON formatiga o'zgartirish va qaytarish
        headers = self.get_success_headers(serializer.data)
        return Response(serializer_info.data, status=status.HTTP_200_OK, headers=headers)


class SmartNoteDestroyView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)  # Foydalanuvchiga ruxsat berilgan ishlar
    serializer_class = CustomIdSerializer  # Serializer uchun qo'llaniladigan klass

    def post(self, request, *args, **kwargs):
        # Serializer obyektini yaratish va ma'lumotlarni tekshirish
        serializer = CustomIdSerializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)

        # lookup_url_kwarg ni aniqlash
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        # Filterni tayyorlash
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        
        # Agar foydalanuvchi tizimga kirgan bo'lsa
        if self.request.user.is_authenticated:
            queryset = Q(user=self.request.user)
        else:
            # Agar foydalanuvchi tizimga kirmagan bo'lsa
            custom_id = serializer.validated_data.get('custom_id')
            if custom_id != '':
                queryset = Q(custom_id=custom_id)
            else:
                queryset = Q(user__id=-985)  # user__id=-985 da SmartNote obyekti mavjud emas

        # Ma'lumotlarni olish
        instance = SmartNote.objects.filter(queryset, **filter_kwargs).first()
        
        # Agar obyekt topilsa, uni o'chirish
        if instance is not None:
            instance.delete()
        
        # Ma'lumotlarni JSON formatiga o'zgartirish va qaytarish
        return Response(status=status.HTTP_204_NO_CONTENT)



class SmartNoteUpdateView(generics.CreateAPIView):
    serializer_class = SmartNoteUpdateSerializer
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        # Ma'lumotlarni olish
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # URL da o'zgaruvchilarni qidirish
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )

        # Filtrlash uchun query ni tayyorlash
        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}

        # Foydalanuvchi tizimga kirdimi yoki yo'qmi tekshirish
        if self.request.user.is_authenticated:
            queryset = Q(user=self.request.user)
        else:
            # Serializerdan custom_id olish
            custom_id = serializer.validated_data.get('custom_id')
            if custom_id != '':
                queryset = Q(custom_id=custom_id)
            else:
                queryset = Q(user__id=-985)

        # Ma'lum bir yozuvni topish
        instance = SmartNote.objects.filter(queryset, **filter_kwargs).first()

        # Agar yozuv topilsa
        if instance:
            # Ma'lumotlarni yangilash
            for key, value in serializer.validated_data.items():
                setattr(instance, key, value)
            instance.save()

        # Yangilangan ma'lumotlarni seriylash
        serializer_info = SmartNoteUpdateSerializer(instance)

        # Javob qaytarish
        headers = self.get_success_headers(serializer.data)
        return Response(serializer_info.data, status=status.HTTP_200_OK, headers=headers)