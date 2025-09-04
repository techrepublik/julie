from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes

from accounts.models import Country, Region, Province, City, Barangay
from accounts.serializers import (
    CountrySerializer,
    RegionSerializer,
    ProvinceSerializer,
    CitySerializer,
    BarangaySerializer
)

import logging

logger = logging.getLogger(__name__)


@extend_schema_view(
    list=extend_schema(
        summary="List all Countries",
        description="Returns a paginated list of all Countries in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter countries by name (partial match)",
                required=False
            ),
            OpenApiParameter(
                name="code",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter countries by country code",
                required=False
            ),
        ],
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": "Philippines",
                            "code": "PH",
                            "created_at": "2025-08-31T17:00:00Z",
                            "updated_at": "2025-08-31T17:00:00Z"
                        }
                    ]
                }
            )
        ],
        tags=["Address Lookup - Countries"]
    ),
    create=extend_schema(
        summary="Create a new Country",
        description="Create a new Country entry.",
        request=CountrySerializer,
        responses={
            201: CountrySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create Country Request',
                value={
                    "name": "Philippines",
                    "code": "PH"
                }
            )
        ],
        tags=["Address Lookup - Countries"]
    ),
    retrieve=extend_schema(
        summary="Get Country details",
        description="Retrieve detailed information for a specific Country.",
        responses={
            200: CountrySerializer,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Countries"]
    ),
    update=extend_schema(
        summary="Update Country information",
        description="Update Country information.",
        request=CountrySerializer,
        responses={
            200: CountrySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Countries"]
    ),
    partial_update=extend_schema(
        summary="Partially update Country information",
        description="Partially update Country information.",
        request=CountrySerializer,
        responses={
            200: CountrySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Countries"]
    ),
    destroy=extend_schema(
        summary="Delete Country",
        description="Delete a Country entry.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Countries"]
    ),
)
class CountryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Country entities.

    Provides CRUD operations for Country entities including:
    - List all countries with filtering options
    - Create new country entries
    - Retrieve country details
    - Update country information
    - Delete country entries
    """
    queryset = Country.objects.all()
    serializer_class = CountrySerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = Country.objects.all()

        # Filter by name
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by code
        code = self.request.query_params.get('code', None)
        if code:
            queryset = queryset.filter(code__icontains=code)

        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Country queryset filtered: {queryset.count()} results by user: {user_info}")
        return queryset

    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        country = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"New country created: {country.id} - {country.name} by user: {user_info}")
        return country

    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        country = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Country updated: {country.id} - {country.name} by user: {user_info}")
        return country

    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        country_name = instance.name
        country_id = instance.id
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        instance.delete()
        logger.info(f"Country deleted: {country_id} - {country.name} by user: {user_info}")

    @extend_schema(
        summary="Get country regions",
        description="Retrieve all regions associated with a specific country.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Countries"]
    )
    @action(detail=True, methods=['get'], url_path='regions')
    def regions(self, request, id=None):
        """
        Get all regions for a specific country.
        """
        try:
            country = self.get_object()
            regions = Region.objects.filter(country=country)
            region_serializer = RegionSerializer(regions, many=True)

            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.info(f"Regions retrieved for country: {country.name} by user: {user_info}")
            return Response({
                "country": country.name,
                "regions": region_serializer.data
            })

        except Country.DoesNotExist:
            return Response(
                {"error": "Country not found"},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List all Regions",
        description="Returns a paginated list of all Regions in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter regions by name (partial match)",
                required=False
            ),
            OpenApiParameter(
                name="country",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter regions by country ID",
                required=False
            ),
        ],
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": "NCR",
                            "country": {
                                "id": 1,
                                "name": "Philippines",
                                "code": "PH"
                            },
                            "created_at": "2025-08-31T17:00:00Z",
                            "updated_at": "2025-08-31T17:00:00Z"
                        }
                    ]
                }
            )
        ],
        tags=["Address Lookup - Regions"]
    ),
    create=extend_schema(
        summary="Create a new Region",
        description="Create a new Region entry.",
        request=RegionSerializer,
        responses={
            201: RegionSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create Region Request',
                value={
                    "name": "NCR",
                    "country": 1
                }
            )
        ],
        tags=["Address Lookup - Regions"]
    ),
    retrieve=extend_schema(
        summary="Get Region details",
        description="Retrieve detailed information for a specific Region.",
        responses={
            200: RegionSerializer,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Regions"]
    ),
    update=extend_schema(
        summary="Update Region information",
        description="Update Region information.",
        request=RegionSerializer,
        responses={
            200: RegionSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Regions"]
    ),
    partial_update=extend_schema(
        summary="Partially update Region information",
        description="Partially update Region information.",
        request=RegionSerializer,
        responses={
            200: RegionSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Regions"]
    ),
    destroy=extend_schema(
        summary="Delete Region",
        description="Delete a Region entry.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Regions"]
    ),
)
class RegionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Region entities.

    Provides CRUD operations for Region entities including:
    - List all regions with filtering options
    - Create new region entries
    - Retrieve region details
    - Update region information
    - Delete region entries
    """
    queryset = Region.objects.select_related('country').all()
    serializer_class = RegionSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = Region.objects.select_related('country').all()

        # Filter by name
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by country
        country = self.request.query_params.get('country', None)
        if country:
            queryset = queryset.filter(country_id=country)

        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Region queryset filtered: {queryset.count()} results by user: {user_info}")
        return queryset

    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        region = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"New region created: {region.id} - {region.name} by user: {user_info}")
        return region

    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        region = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Region updated: {region.id} - {region.name} by user: {user_info}")
        return region

    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        region_name = instance.name
        region_id = instance.id
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        instance.delete()
        logger.info(f"Region deleted: {region_id} - {region_name} by user: {user_info}")

    @extend_schema(
        summary="Get region provinces",
        description="Retrieve all provinces associated with a specific region.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Regions"]
    )
    @action(detail=True, methods=['get'], url_path='provinces')
    def provinces(self, request, id=None):
        """
        Get all provinces for a specific region.
        """
        try:
            region = self.get_object()
            provinces = Province.objects.filter(region=region)
            province_serializer = ProvinceSerializer(provinces, many=True)

            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.info(f"Provinces retrieved for region: {region.name} by user: {user_info}")
            return Response({
                "region": region.name,
                "provinces": province_serializer.data
            })

        except Region.DoesNotExist:
            return Response(
                {"error": "Region not found"},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List all Provinces",
        description="Returns a paginated list of all Provinces in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter provinces by name (partial match)",
                required=False
            ),
            OpenApiParameter(
                name="region",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter provinces by region ID",
                required=False
            ),
        ],
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": "Metro Manila",
                            "region": {
                                "id": 1,
                                "name": "NCR",
                                "country": {
                                    "id": 1,
                                    "name": "Philippines",
                                    "code": "PH"
                                }
                            },
                            "created_at": "2025-08-31T17:00:00Z",
                            "updated_at": "2025-08-31T17:00:00Z"
                        }
                    ]
                }
            )
        ],
        tags=["Address Lookup - Provinces"]
    ),
    create=extend_schema(
        summary="Create a new Province",
        description="Create a new Province entry.",
        request=ProvinceSerializer,
        responses={
            201: ProvinceSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create Province Request',
                value={
                    "name": "Metro Manila",
                    "region": 1
                }
            )
        ],
        tags=["Address Lookup - Provinces"]
    ),
    retrieve=extend_schema(
        summary="Get Province details",
        description="Retrieve detailed information for a specific Province.",
        responses={
            200: ProvinceSerializer,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Provinces"]
    ),
    update=extend_schema(
        summary="Update Province information",
        description="Update Province information.",
        request=ProvinceSerializer,
        responses={
            200: ProvinceSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Provinces"]
    ),
    partial_update=extend_schema(
        summary="Partially update Province information",
        description="Partially update Province information.",
        request=ProvinceSerializer,
        responses={
            200: ProvinceSerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Provinces"]
    ),
    destroy=extend_schema(
        summary="Delete Province",
        description="Delete a Province entry.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Provinces"]
    ),
)
class ProvinceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Province entities.

    Provides CRUD operations for Province entities including:
    - List all provinces with filtering options
    - Create new province entries
    - Retrieve province details
    - Update province information
    - Delete province entries
    """
    queryset = Province.objects.select_related('region__country').all()
    serializer_class = ProvinceSerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = Province.objects.select_related('region__country').all()

        # Filter by name
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by region
        region = self.request.query_params.get('region', None)
        if region:
            queryset = queryset.filter(region_id=region)

        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Province queryset filtered: {queryset.count()} results by user: {user_info}")
        return queryset

    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        province = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"New province created: {province.id} - {province.name} by user: {user_info}")
        return province

    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        province = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Province updated: {province.id} - {province.name} by user: {user_info}")
        return province

    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        province_name = instance.name
        province_id = instance.id
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        instance.delete()
        logger.info(f"Province deleted: {province_id} - {province_name} by user: {user_info}")

    @extend_schema(
        summary="Get province cities",
        description="Retrieve all cities associated with a specific province.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Provinces"]
    )
    @action(detail=True, methods=['get'], url_path='cities')
    def cities(self, request, id=None):
        """
        Get all cities for a specific province.
        """
        try:
            province = self.get_object()
            cities = City.objects.filter(province=province)
            city_serializer = CitySerializer(cities, many=True)

            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.info(f"Cities retrieved for province: {province.name} by user: {user_info}")
            return Response({
                "province": province.name,
                "cities": city_serializer.data
            })

        except Province.DoesNotExist:
            return Response(
                {"error": "Province not found"},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List all Cities",
        description="Returns a paginated list of all Cities in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter cities by name (partial match)",
                required=False
            ),
            OpenApiParameter(
                name="province",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter cities by province ID",
                required=False
            ),
        ],
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": "Manila",
                            "province": {
                                "id": 1,
                                "name": "Metro Manila",
                                "region": {
                                    "id": 1,
                                    "name": "NCR",
                                    "country": {
                                        "id": 1,
                                        "name": "Philippines",
                                        "code": "PH"
                                    }
                                }
                            },
                            "created_at": "2025-08-31T17:00:00Z",
                            "updated_at": "2025-08-31T17:00:00Z"
                        }
                    ]
                }
            )
        ],
        tags=["Address Lookup - Cities"]
    ),
    create=extend_schema(
        summary="Create a new City",
        description="Create a new City entry.",
        request=CitySerializer,
        responses={
            201: CitySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create City Request',
                value={
                    "name": "Manila",
                    "province": 1
                }
            )
        ],
        tags=["Address Lookup - Cities"]
    ),
    retrieve=extend_schema(
        summary="Get City details",
        description="Retrieve detailed information for a specific City.",
        responses={
            200: CitySerializer,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Cities"]
    ),
    update=extend_schema(
        summary="Update City information",
        description="Update City information.",
        request=CitySerializer,
        responses={
            200: CitySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Cities"]
    ),
    partial_update=extend_schema(
        summary="Partially update City information",
        description="Partially update City information.",
        request=CitySerializer,
        responses={
            200: CitySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Cities"]
    ),
    destroy=extend_schema(
        summary="Delete City",
        description="Delete a City entry.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Cities"]
    ),
)
class CityViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing City entities.

    Provides CRUD operations for City entities including:
    - List all cities with filtering options
    - Create new city entries
    - Retrieve city details
    - Update city information
    - Delete city entries
    """
    queryset = City.objects.select_related('province__region__country').all()
    serializer_class = CitySerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = City.objects.select_related('province__region__country').all()

        # Filter by name
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by province
        province = self.request.query_params.get('province', None)
        if province:
            queryset = queryset.filter(province_id=province)

        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"City queryset filtered: {queryset.count()} results by user: {user_info}")
        return queryset

    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        city = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"New city created: {city.id} - {city.name} by user: {user_info}")
        return city

    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        city = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"City updated: {city.id} - {city.name} by user: {user_info}")
        return city

    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        city_name = instance.name
        city_id = instance.id
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        instance.delete()
        logger.info(f"City deleted: {city_id} - {city_name} by user: {user_info}")

    @extend_schema(
        summary="Get city barangays",
        description="Retrieve all barangays associated with a specific city.",
        responses={
            200: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Cities"]
    )
    @action(detail=True, methods=['get'], url_path='barangays')
    def barangays(self, request, id=None):
        """
        Get all barangays for a specific city.
        """
        try:
            city = self.get_object()
            barangays = Barangay.objects.filter(city=city)
            barangay_serializer = BarangaySerializer(barangays, many=True)

            user_info = self.request.user.get_full_name() or self.request.user.mobile_no
            logger.info(f"Barangays retrieved for city: {city.name} by user: {user_info}")
            return Response({
                "city": city.name,
                "barangays": barangay_serializer.data
            })

        except City.DoesNotExist:
            return Response(
                {"error": "City not found"},
                status=status.HTTP_404_NOT_FOUND
            )


@extend_schema_view(
    list=extend_schema(
        summary="List all Barangays",
        description="Returns a paginated list of all Barangays in the system with optional filtering.",
        parameters=[
            OpenApiParameter(
                name="name",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filter barangays by name (partial match)",
                required=False
            ),
            OpenApiParameter(
                name="city",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="Filter barangays by city ID",
                required=False
            ),
        ],
        examples=[
            OpenApiExample(
                'Success Response',
                value={
                    "count": 1,
                    "next": None,
                    "previous": None,
                    "results": [
                        {
                            "id": 1,
                            "name": "Barangay 1",
                            "city": {
                                "id": 1,
                                "name": "Manila",
                                "province": {
                                    "id": 1,
                                    "name": "Metro Manila",
                                    "region": {
                                        "id": 1,
                                        "name": "NCR",
                                        "country": {
                                            "id": 1,
                                            "name": "Philippines",
                                            "code": "PH"
                                        }
                                    }
                                }
                            },
                            "created_at": "2025-08-31T17:00:00Z",
                            "updated_at": "2025-08-31T17:00:00Z"
                        }
                    ]
                }
            )
        ],
        tags=["Address Lookup - Barangays"]
    ),
    create=extend_schema(
        summary="Create a new Barangay",
        description="Create a new Barangay entry.",
        request=BarangaySerializer,
        responses={
            201: BarangaySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
        },
        examples=[
            OpenApiExample(
                'Create Barangay Request',
                value={
                    "name": "Barangay 1",
                    "city": 1
                }
            )
        ],
        tags=["Address Lookup - Barangays"]
    ),
    retrieve=extend_schema(
        summary="Get Barangay details",
        description="Retrieve detailed information for a specific Barangay.",
        responses={
            200: BarangaySerializer,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Barangays"]
    ),
    update=extend_schema(
        summary="Update Barangay information",
        description="Update Barangay information.",
        request=BarangaySerializer,
        responses={
            200: BarangaySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Barangays"]
    ),
    partial_update=extend_schema(
        summary="Partially update Barangay information",
        description="Partially update Barangay information.",
        request=BarangaySerializer,
        responses={
            200: BarangaySerializer,
            400: OpenApiTypes.OBJECT,
            401: OpenApiTypes.OBJECT,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Barangays"]
    ),
    destroy=extend_schema(
        summary="Delete Barangay",
        description="Delete a Barangay entry.",
        responses={
            204: None,
            404: OpenApiTypes.OBJECT,
        },
        tags=["Address Lookup - Barangays"]
    ),
)
class BarangayViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing Barangay entities.

    Provides CRUD operations for Barangay entities including:
    - List all barangays with filtering options
    - Create new barangay entries
    - Retrieve barangay details
    - Update barangay information
    - Delete barangay entries
    """
    queryset = Barangay.objects.select_related('city__province__region__country').all()
    serializer_class = BarangaySerializer
    lookup_field = 'id'

    def get_queryset(self):
        """
        Custom queryset with optional filtering.
        """
        queryset = Barangay.objects.select_related('city__province__region__country').all()

        # Filter by name
        name = self.request.query_params.get('name', None)
        if name:
            queryset = queryset.filter(name__icontains=name)

        # Filter by city
        city = self.request.query_params.get('city', None)
        if city:
            queryset = queryset.filter(city_id=city)

        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Barangay queryset filtered: {queryset.count()} results by user: {user_info}")
        return queryset

    def perform_create(self, serializer):
        """
        Custom create logic with logging.
        """
        barangay = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"New barangay created: {barangay.id} - {barangay.name} by user: {user_info}")
        return barangay

    def perform_update(self, serializer):
        """
        Custom update logic with logging.
        """
        barangay = serializer.save()
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        logger.info(f"Barangay updated: {barangay.id} - {barangay.name} by user: {user_info}")
        return barangay

    def perform_destroy(self, instance):
        """
        Custom delete logic with logging.
        """
        barangay_name = instance.name
        barangay_id = instance.id
        user_info = self.request.user.get_full_name() or self.request.user.mobile_no
        instance.delete()
        logger.info(f"Barangay deleted: {barangay_id} - {barangay_name} by user: {user_info}")
