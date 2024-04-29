from django.http import Http404
from rest_framework import generics, status
from rest_framework.response import Response
from django.db.models import Q
from all_data.models import InformativeData, ObjectPhoto, Status
from api.permissions import IsLegal
from informative_data.serializers import InformativeDataDraftSerializer, InformativeDataGetSerializer, InformativeProDataSerializer, ObjectPhotoSerializer

class InformativeDataView(generics.RetrieveUpdateAPIView):
    serializer_class = InformativeProDataSerializer
    permission_classes = (IsLegal,)

    def get_object(self):
        queryset = InformativeData.objects.filter(user=self.request.user, all_data__status=Status.DRAFT)
        try:
            instance = queryset.first()
        except InformativeData.DoesNotExist:
            raise Http404("No matching InformativeData found for this user")
        return instance

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class InformativeDataDraftRetrieveView(generics.RetrieveAPIView):
    serializer_class = InformativeDataGetSerializer
    permission_classes = (IsLegal,)

    def get_object(self):
        return InformativeData.objects.filter(Q(all_data__status=Status.DRAFT) & Q(user=self.request.user)).first()
    

class ObjectPhotoView(generics.CreateAPIView):
    serializer_class = ObjectPhotoSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        instance = InformativeData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        ObjectPhoto.objects.create(
            image=serializer.validated_data['image'],
            informative_data=instance
        )


class InformativeDataDraftView(generics.CreateAPIView):
    serializer_class = InformativeDataDraftSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        instance = InformativeData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()