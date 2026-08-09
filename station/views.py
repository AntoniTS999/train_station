from datetime import datetime

from django.db.models import Count, F
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ModelViewSet
from station.models import Train, Journey, Order, Ticket
from station.serializers import (TrainSerializer,
                                 JourneySerializer,
                                 JourneyListSerializer,
                                 JourneyDetailSerializer,
                                 OrderSerializer,
                                 OrderDetailSerializer, OrderListSerializer)


class TrainViewSet(ModelViewSet):
    serializer_class = TrainSerializer
    queryset = Train.objects.all()

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return Train.objects.all().select_related("train_type")
        else:
            return Train.objects.all()


class JourneyViewSet(ModelViewSet):
    queryset = Journey.objects.all().select_related("route",
                                                        "route__source",
                                                        "route__destination",
                                                        "train",
                                                        "train__train_type").prefetch_related("crew")

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

            if source_filter:
                queryset = queryset.filter(route__source__name__icontains=source_filter)
            if destination_filter:
                queryset = queryset.filter(route__destination__name__icontains=destination_filter)

            return queryset.annotate(available=F("train__cargo_num") * F("train__places_in_cargo") - Count("tickets"))
        else:
            return queryset.annotate(taken=Count("tickets"))


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user)
        if self.action in ["list", "retrieve"]:
            return qs.prefetch_related("tickets__journey__train",
                                       "tickets__journey__route__source",
                                       "tickets__journey__route__destination")
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


