from django.http import Http404
from rest_framework import generics, status, permissions, views, mixins, viewsets
from rest_framework.response import Response
from django.db.models import Q, Case, When, Value, F, DecimalField, Subquery
from django.utils.decorators import method_decorator
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from all_data.models import AllData, CurrencyPrice, InvestorInfo, Status
from all_data.serializers import AllDataAllUsersListSerializer, AllDataFilterSerializer, AllDataListSerializer, AllDataSerializer, AlldateCategorySerializer, ApproveRejectInvestorSerializer, InvestorInfoGetMinimumSerializer, InvestorInfoGetSerializer, InvestorInfoOwnSerializer, InvestorInfoSerializer
from api.permissions import IsLegal


class AllDataCatListAPIView(generics.ListAPIView):
    queryset = AllData.objects.all()
    serializer_class = AlldateCategorySerializer
    permission_classes = (permissions.AllowAny,)



class AllDataViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AllData.objects.filter(status=Status.APPROVED)
    permission_classes = (permissions.AllowAny,)
    serializer_class = AllDataSerializer


class AllDataUserViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AllData.objects.all()
    permission_classes = (IsLegal,)
    # serializer_class = AllDataListSerializer
    default_serializer_class = AllDataSerializer
    serializer_classes = {
        'list': AllDataListSerializer,
        'retrieve': AllDataSerializer
    }

    def get_queryset(self):
        return AllData.objects.filter(~Q(status=Status.DRAFT) & Q(user=self.request.user))

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class AllDataUserViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AllData.objects.all()
    permission_classes = (IsLegal,)
    # serializer_class = AllDataListSerializer
    default_serializer_class = AllDataSerializer
    serializer_classes = {
        'list': AllDataListSerializer,
        'retrieve': AllDataSerializer
    }

    def get_queryset(self):
        return AllData.objects.filter(~Q(status=Status.DRAFT) & Q(user=self.request.user))

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)


class AllDataAllUsersViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = AllData.objects.all()
    permission_classes = (IsLegal,)
    # serializer_class = AllDataListSerializer
    default_serializer_class = AllDataSerializer
    serializer_classes = {
        'list': AllDataAllUsersListSerializer,
        'retrieve': AllDataSerializer
    }

    def get_queryset(self):
        return AllData.objects.filter(Q(status=Status.APPROVED))

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)
    


class CustomAlldataAllUsersListView(generics.ListAPIView):
    queryset = AllData.objects.filter(Q(status=Status.APPROVED))
    serializer_class = AllDataAllUsersListSerializer
    permission_classes = (permissions.AllowAny,)

    def list(self, request, *args, **kwargs):
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field
        assert lookup_url_kwarg in self.kwargs, (
                'Expected view %s to be called with a URL keyword argument '
                'named "%s". Fix your URL conf, or set the `.lookup_field` '
                'attribute on the view correctly.' %
                (self.__class__.__name__, lookup_url_kwarg)
        )
        filter_kwargs = {'main_data__category__id': self.kwargs[lookup_url_kwarg]}
        queryset = self.queryset.filter(**filter_kwargs)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    






class InvestorInfoView(generics.CreateAPIView):
    serializer_class = InvestorInfoSerializer
    permission_classes = (IsLegal,)

    def perform_create(self, serializer):
        all_data = AllData.objects.filter(
            Q(id=serializer.validated_data['all_data'].id) &
            Q(status=Status.APPROVED)
        )

        if all_data.exists():
            instance = InvestorInfo.objects.create(
                investor=self.request.user,
                status=Status.APPROVED,
                all_data=all_data.first()
            )

            for key, value in serializer.validated_data.items():
                if not key == 'all_data':
                    setattr(instance, key, value)
            instance.save()


class InvestorInfoViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = InvestorInfo.objects.all()
    permission_classes = (IsLegal,)
    serializer_class = InvestorInfoGetSerializer

    def get_queryset(self):
        return InvestorInfo.objects.filter(
            Q(status=Status.APPROVED) &
            Q(all_data__user=self.request.user)
        )


user_id = openapi.Parameter(
    'user_id', openapi.IN_QUERY,
    description="If user_id exists, return investors for this user, else return investors for current user",
    type=openapi.TYPE_STRING
)


@method_decorator(name='list', decorator=swagger_auto_schema(manual_parameters=[
    user_id,
]))
class AllObjectInvestorsViewSet(viewsets.GenericViewSet, mixins.ListModelMixin, mixins.RetrieveModelMixin):
    queryset = InvestorInfo.objects.all()
    permission_classes = (IsLegal,)
    # serializer_class = InvestorInfoGetSerializer
    default_serializer_class = InvestorInfoGetSerializer
    serializer_classes = {
        'list': InvestorInfoGetMinimumSerializer,
        'retrieve': InvestorInfoGetSerializer
    }

    def get_serializer_class(self):
        return self.serializer_classes.get(self.action, self.default_serializer_class)

    def get_queryset(self):
        data = self.request.GET.dict()
        queryset = ~Q(status=Status.DRAFT)
        if 'user_id' in data:
            queryset &= Q(all_data__user__id=data['user_id'])
        else:
            queryset &= Q(all_data__user=self.request.user)
        return InvestorInfo.objects.filter(queryset)
    

class ApproveRejectView(generics.CreateAPIView):
    serializer_class = ApproveRejectInvestorSerializer
    permission_classes = (IsLegal,)

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            investor = InvestorInfo.objects.filter(
                Q(id=serializer.validated_data['investor_id']) &
                Q(all_data__id=serializer.validated_data['all_data_id'])
            )
            if investor.exists():
                investor = investor.first()
                if serializer.validated_data['is_approve']:
                    investor.status = Status.APPROVED
                else:
                    investor.status = Status.REJECTED
                investor.save(force_update=True)
                return Response(serializer.validated_data)
            else:
                return Response({'error': 'Investor or object does not exist'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class InvestorInfoOwnListView(generics.ListAPIView):
    queryset = InvestorInfo.objects.all()
    serializer_class = InvestorInfoOwnSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        return InvestorInfo.objects.filter(investor=self.request.user)


categories = openapi.Parameter(
    'categories', openapi.IN_QUERY,
    description="Filter objects by array of categories id. Example: categories=1,2",
    type=openapi.TYPE_STRING
)


@method_decorator(name='get', decorator=swagger_auto_schema(manual_parameters=[
    categories,
]))
class AllDataFilterView(generics.ListAPIView):
    serializer_class = AllDataFilterSerializer
    permission_classes = (permissions.AllowAny,)

    # pagination_class = TenPagesPagination

    def get_queryset(self):
        data = self.request.GET.dict()
        queryset = Q(status=Status.APPROVED)
        if 'categories' in data:
            category_list = []
            for category in data['categories'].split(','):
                category_list.append(int(category))
            queryset &= Q(main_data__category__pk__in=category_list)
        if 'locations' in data:
            location_list = []
            for location in data['locations'].split(','):
                location_list.append(int(location))
            queryset &= Q(main_data__location__pk__in=location_list)
        if 'startprice' in data and 'endprice' in data:
            queryset &= Q(new_price_dollar__gte=int(data['startprice']), new_price_dollar__lte=int(data['endprice']))
        elif int(data['startprice']) == 100000:
            queryset &= Q(new_price_dollar__gte=int(data['startprice']))

        datas = AllData.objects.annotate(
            latest_gbp_price=Subquery(CurrencyPrice.objects.filter(code='EUR').order_by('-date').values('cb_price')[:1],
                                      output_field=DecimalField(max_digits=18, decimal_places=2)),
            latest_eur_price=Subquery(CurrencyPrice.objects.filter(code='EUR').order_by('-date').values('cb_price')[:1],
                                      output_field=DecimalField(max_digits=18, decimal_places=2)),
            latest_usd_price=Subquery(CurrencyPrice.objects.filter(code='USD').order_by('-date').values('cb_price')[:1],
                                      output_field=DecimalField(max_digits=18, decimal_places=2)),
        ).annotate(
            new_price_dollar=Case(
                When(financial_data__currency__code='GBP',
                     then=F('financial_data__authorized_capital') * F('latest_gbp_price') / F('latest_usd_price')),
                When(financial_data__currency__code='EUR',
                     then=F('financial_data__authorized_capital') * F('latest_eur_price') / F('latest_usd_price')),
                When(financial_data__currency__code='UZS',
                     then=F('financial_data__authorized_capital') / F('latest_usd_price')),
                When(financial_data__currency__code='USD',
                     then=F('financial_data__authorized_capital') * F('latest_usd_price') / F('latest_usd_price')),
                default=F('financial_data__authorized_capital'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        ).filter(queryset)
        return datas


import math

lat_long = openapi.Parameter(
    'lat_long', openapi.IN_QUERY,
    description="Filter objects by latitude and longitude. Example: lat_long=21.1234,22.4321",
    type=openapi.TYPE_STRING
)
distance_km = openapi.Parameter(
    'distance', openapi.IN_QUERY,
    description="Filter objects by radius in km from latitude and longitude. Example: distance=10. Default distance 50 km",
    type=openapi.TYPE_STRING
)


@method_decorator(name='get', decorator=swagger_auto_schema(manual_parameters=[
    lat_long, distance_km
]))
class AllDataFilterByLatLongDistanceView(generics.ListAPIView):
    serializer_class = AllDataFilterSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        data = self.request.GET.dict()
        queryset = Q(status=Status.APPROVED)

        distance = 50.0
        earth_radius = 6371.0
        if 'distance' in data:
            distance = float(data['distance']) if distance <= earth_radius else earth_radius

        if 'lat_long' in data:
            lat_long_list = data['lat_long'].split(',')
            if len(lat_long_list) == 2:
                lat = float(lat_long_list[0])
                long = float(lat_long_list[1])
                max_lat = lat + math.degrees(distance / earth_radius)
                min_lat = lat - math.degrees(distance / earth_radius)
                max_long = long + math.degrees(math.asin(distance / earth_radius) / math.cos(math.radians(lat)))
                min_long = long - math.degrees(math.asin(distance / earth_radius) / math.cos(math.radians(lat)))
                # log(f'min_lat: {min_lat} max_lat: {max_lat} min_long: {min_long} max_long: {max_long}')
                queryset &= Q(main_data__lat__gte=min_lat)
                queryset &= Q(main_data__lat__lte=max_lat)
                queryset &= Q(main_data__long__gte=min_long)
                queryset &= Q(main_data__long__lte=max_long)
                return AllData.objects.filter(queryset)
            else:
                return []
        return []