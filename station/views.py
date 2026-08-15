from datetime import datetime

from django.db.models import Count, F
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema, OpenApiParameter
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import UserRateThrottle, ScopedRateThrottle
from rest_framework.viewsets import ModelViewSet
from station.models import Train, Journey, Order, Ticket
from station.pagination import OrderPagination
from station.serializers import (TrainSerializer,
                                 JourneySerializer,
                                 JourneyListSerializer,
                                 JourneyDetailSerializer,
                                 OrderSerializer,
                                 OrderDetailSerializer,
                                 OrderListSerializer,
                                 TrainImageSerializer,
                                 TrainListSerializer)


class IsAuthenticatedReadOnlyOrAdmin(BasePermission):
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        if request.user and request.user.is_authenticated and request.user.is_staff:
            return True
        return False

class TrainViewSet(ModelViewSet):
    serializer_class = TrainSerializer
    queryset = Train.objects.all()
    throttle_scope = "train_view"
    throttle_classes = [ScopedRateThrottle]
    permission_classes = [IsAuthenticatedReadOnlyOrAdmin]


    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return Train.objects.all().select_related("train_type")
        else:
            return Train.objects.all()

    @action(methods=["POST"], detail=True, url_path="upload_image", url_name="upload_image",     parser_classes=[MultiPartParser, FormParser],)
    def upload_image(self, request, **kwargs):
        train = self.get_object()
        serializer = self.get_serializer_class()(train, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return TrainListSerializer
        if self.action == "upload_image":
            return TrainImageSerializer
        else:
            return self.serializer_class
class JourneyViewSet(ModelViewSet):
    queryset = Journey.objects.all().select_related("route",
                                                        "route__source",
                                                        "route__destination",
                                                        "train",
                                                        "train__train_type").prefetch_related("crew")
    permission_classes = [IsAuthenticatedReadOnlyOrAdmin]

    def get_serializer_class(self):
        if self.action in ["list"]:
            return JourneyListSerializer
        elif self.action in ["retrieve"]:
            return JourneyDetailSerializer
        else:
            return JourneySerializer

    def get_queryset(self):
        queryset = self.queryset
        if self.action in ["list"]:
            train_type_filter = self.request.query_params.get("train", None)
            date_filter = self.request.query_params.get("date", None)
            source_filter = self.request.query_params.get("source", None)
            destination_filter = self.request.query_params.get("destination", None)

            if train_type_filter:
                queryset = queryset.filter(train__train_type__name__icontains=train_type_filter)

            if date_filter:
                try:
                    date_filter = datetime.strptime(date_filter, "%Y-%m-%d").date()
                except ValueError:
                    raise ValidationError("Please provide a valid date in YYYY-MM-DD format")
                queryset = queryset.filter(departure_time__date=date_filter)

            if source_filter and destination_filter:
                queryset = queryset.filter(route__source__name__icontains=source_filter, route__destination__name__icontains=destination_filter)

            return queryset.annotate(available=F("train__cargo_num") * F("train__places_in_cargo") - Count("tickets"))
        else:
            return queryset.annotate(taken=Count("tickets"))

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="date",
                type=OpenApiTypes.STR,
                description="The date to filter by",
            ),
            OpenApiParameter(
                name="source",
                type=OpenApiTypes.STR,
                description="The source to filter by",
            ),
            OpenApiParameter(
                name="destination",
                type=OpenApiTypes.STR,
                description="The destination to filter by",
            ),
            OpenApiParameter(
                name="train",
                type=OpenApiTypes.STR,
                description="The train to filter by",
            )
        ]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    pagination_class = OrderPagination
    http_method_names = ["get", "post", "delete", "head", "options"]
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user)
        if self.action in ["list", "retrieve"]:
            return qs.prefetch_related("tickets__journey__train",
                                       "tickets__journey__route__source",
                                       "tickets__journey__route__destination",
                                       "tickets__journey__crew",)
        else:
            return qs.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "list":
            return OrderListSerializer
        if self.action == "retrieve":
            return OrderDetailSerializer
        else:
            return self.serializer_class


