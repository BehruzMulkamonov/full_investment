from django.http import Http404
from rest_framework import generics, status, permissions, viewsets, mixins
from rest_framework.response import Response
from django.db.models import Q
from all_data.models import AllData, Area, Category, Currency, FinancialData, InformativeData, MainData, ObjectPhoto, Status
from all_data.serializers import AlldateCategorySerializer, ObjectIdAndCoordinatesSerializer
from api.permissions import IsLegal
from informative_data.serializers import ObjectPhotoSerializer
from main_data.serializers import AreaAPISerializer, AreaSerializer, CategoryApiProSerializer, CategorySerializer, LocationSerializer, MainDataAPISerializer, MainDataDraftSerializer, MainDataRetrieveSerializer, MainDataSerializer
from geopy.geocoders import Nominatim


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (permissions.AllowAny,)


class AreaListView(generics.ListAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaSerializer
    permission_classes = (permissions.AllowAny,)


class AreaAPIListView(generics.ListAPIView):
    queryset = Area.objects.all()
    serializer_class = AreaAPISerializer
    # permission_classes = (permissions.AllowAny,)


class CategoryApiListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryApiProSerializer
    permission_classes = (permissions.AllowAny,)


class CategoryRetrieveView(generics.RetrieveAPIView):
    queryset = Category.objects.all()
    serializer_class = CategoryApiProSerializer
    permission_classes = (permissions.AllowAny,)

    def get(self, request, *args, **kwargs):
        queryset = AllData.objects.all()  # Sizning queryset
        serializer = AlldateCategorySerializer()
        return Response(serializer.data)



class MainDataAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = MainDataAPISerializer
    permission_classes = (IsLegal,)
    lookup_field = 'user'

    def get_object(self):
        queryset = MainData.objects.filter(user=self.request.user, all_data__status=Status.DRAFT)
        try:
            instance = queryset.first()
        except MainData.DoesNotExist:
            raise Http404("No matching MainData found for this user")
        return instance

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


class MainDataView(generics.CreateAPIView):
    serializer_class = MainDataSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        instance = MainData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        instance.is_validated = True
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()



class MainDataDraftRetrieveView(generics.RetrieveAPIView):
    serializer_class = MainDataRetrieveSerializer
    permission_classes = (IsLegal,)

    def get_object(self):
        # return MainData.objects.filter(Q(all_data__status=Status.DRAFT) & Q(user=self.request.user)).first()
        return MainData.objects.all()


class MainDataDraftListView(generics.RetrieveAPIView):
    serializer_class = MainDataRetrieveSerializer
    permission_classes = (IsLegal,)

    def get_object(self):
        queryset = MainData.objects.filter(user=self.request.user)
        try:
            instance = queryset.first()
        except MainData.DoesNotExist:
            raise Http404("No matching MainData found for this user")
        return instance
    

class MainDataDraftView(generics.CreateAPIView):
    serializer_class = MainDataDraftSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        hasnot_instance = False
        instance = MainData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        if instance is None:
            hasnot_instance = True
            instance = MainData(user=self.request.user)
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()
        if hasnot_instance:
            informdata = InformativeData(user=self.request.user)
            informdata.save()
            finandata = FinancialData(user=self.request.user, currency=Currency.objects.first())
            finandata.save()
            all_data = AllData(main_data=instance, informative_data=informdata,
                               financial_data=finandata, user=self.request.user,
                               )
            all_data.save()


class ObjectIdAndCoordinatesViewSet(viewsets.GenericViewSet, mixins.ListModelMixin):
    queryset = AllData.objects.filter(status=Status.APPROVED)
    permission_classes = (permissions.AllowAny,)
    serializer_class = ObjectIdAndCoordinatesSerializer


class LocationView(generics.CreateAPIView):
    serializer_class = LocationSerializer
    permission_classes = (permissions.AllowAny,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            geolocator = Nominatim(user_agent="E-Investment")
            location = geolocator.reverse(f"{serializer.validated_data['lat']}, {serializer.validated_data['long']}")
            return Response(location.address)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class ObjectPhotoViewList(generics.ListAPIView):
    queryset = ObjectPhoto.objects.all()
    serializer_class = ObjectPhotoSerializer
    permission_classes = (permissions.AllowAny,)