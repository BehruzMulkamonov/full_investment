from django.http import Http404
from rest_framework import generics, status, permissions, views, mixins, viewsets
from rest_framework.response import Response
from django.db.models import Q
from ..permissions import IsLegal
from all_data.models import AllData, Currency, FinancialData, InformativeData, MainData, Status
from financial_data.serializers import CurrencySerializer, FinancialDataDraftSerializer, FinancialDataRetrieveSerializer, FinancialDataSerializer
from logs import log


class FinancialDataView(generics.CreateAPIView):
    serializer_class = FinancialDataSerializer
    permission_classes = (IsLegal,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        # log('StartLog')
        if serializer.is_valid():
            instance = FinancialData.objects.filter(
                Q(user=self.request.user) &
                Q(all_data__status=Status.DRAFT)
            ).first()
            instance.is_validated = True
            # setattr(instance, 'is_validated', True)
            for key, value in serializer.validated_data.items():
                setattr(instance, key, value)
            # log(f'is_validated: {instance.is_validated}')
            instance.save()

            all_data = AllData.objects.filter(
                Q(user=self.request.user) &
                Q(status=Status.DRAFT) &
                Q(main_data__is_validated=True) &
                Q(informative_data__is_validated=True) &
                Q(financial_data__is_validated=True)
            )
            # log(f'all_data: {all_data.id}')
            if all_data.exists():
                all_data = all_data.first()
                # all_data.status = Status. # VAXTINCHALIK OZGARTRIB TUSHILGAN SINOV UCHUNCHECKING
                all_data.save()
                log(f'all_data2: {all_data.status}')

                main_data = MainData.objects.create(
                    user=self.request.user,
                )
                informative_data = InformativeData.objects.create(
                    user=self.request.user,
                )
                financial_data = FinancialData.objects.create(
                    user=self.request.user, currency=Currency.objects.first()
                )
                AllData.objects.create(
                    main_data=main_data,
                    informative_data=informative_data,
                    financial_data=financial_data,
                    user=self.request.user
                )
                return Response(serializer.validated_data)
            else:
                return Response({'error': 'Not all data validated'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FinancialDataAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = FinancialDataSerializer

    permission_classes = (IsLegal,)

    def get_object(self):
        queryset = FinancialData.objects.filter(user=self.request.user)
        try:
            instance = queryset.first()
        except FinancialData.DoesNotExist:
            raise Http404("No matching FinancialData found for this user")
        return instance

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            all_data = AllData.objects.filter(
                Q(user=self.request.user) &
                Q(status=Status.DRAFT) &
                Q(main_data__is_validated=True) &
                Q(informative_data__is_validated=True) &
                Q(financial_data__is_validated=True)
            )
            if all_data.exists():
                all_data = all_data.first()
                all_data.status = Status.CHECKING  # VAXTINCHALIK OZGARTRIB TUSHILGAN SINOV UCHUN
                all_data.save()

                main_data = MainData.objects.create(
                    user=self.request.user,
                )
                informative_data = InformativeData.objects.create(
                    user=self.request.user,
                )

                financial_data = FinancialData.objects.create(
                    user=self.request.user,
                    currency=Currency.objects.first()
                )
                AllData.objects.create(
                    main_data=main_data,
                    informative_data=informative_data,
                    financial_data=financial_data,
                    user=self.request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Not all data validated'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class FinancialDataDraftRetrieveView(generics.RetrieveAPIView):
    serializer_class = FinancialDataRetrieveSerializer
    permission_classes = (IsLegal,)

    def get_object(self):
        return FinancialData.objects.filter(Q(all_data__status=Status.DRAFT) & Q(user=self.request.user)).first()
    

class FinancialDataDraftView(generics.CreateAPIView):
    serializer_class = FinancialDataDraftSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        instance = FinancialData.objects.filter(
            Q(user=self.request.user) &
            Q(all_data__status=Status.DRAFT)
        ).first()
        for key, value in serializer.validated_data.items():
            setattr(instance, key, value)
        instance.save()


class CurrencyListView(generics.ListAPIView):
    queryset = Currency.objects.all()
    serializer_class = CurrencySerializer
    permission_classes = (permissions.AllowAny,)