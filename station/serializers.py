from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from station.models import Train, Journey, Crew, Route, Station, Order, Ticket


class TrainImageSerializer(ModelSerializer):
    class Meta:
        model = Train
        fields = ["id", "image"]


class TrainSerializer(ModelSerializer):
    train_type = serializers.CharField(source="train_type.name", read_only=True)
    class Meta:
        model = Train
        fields = ["id", "name", "cargo_num", "places_in_cargo", "train_type", "is_small"]

class CrewSerializer(ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]


class RouteSerializer(ModelSerializer):
    source = serializers.SlugRelatedField(slug_field="name", read_only=True)
    destination = serializers.SlugRelatedField(slug_field="name", read_only=True)
    class Meta:
        model = Route
        fields = ["id", "source", "destination", "distance"]


class JourneySerializer(ModelSerializer):
    class Meta:
        model = Journey
        fields = ["id", "route", "train", "departure_time", "arrival_time", "crew"]


class JourneyListSerializer(ModelSerializer):
    source = serializers.CharField(source="route.source", read_only=True)
    destination = serializers.CharField(source="route.destination", read_only=True)
    train_name = serializers.CharField(source="train.name", read_only=True)
    train_capacity = serializers.CharField(source="train.total_places", read_only=True)
    available_seats = serializers.IntegerField(read_only=True, source="available")
    class Meta:
        model = Journey
        fields = ["id", "source", "destination", "train_name", "train_capacity", "departure_time", "arrival_time", "available_seats", "crew"]


class TicketSerializer(ModelSerializer):
    class Meta:
        model = Ticket
        fields = ["id", "cargo", "seat", "journey" ]

        validators = [
            UniqueTogetherValidator(
                queryset=Ticket.objects.all(),
                fields=["journey", "cargo", "seat"],
                message="Ticket with the same cargo, seat and journey already exists"
            )
        ]
    def validate(self, value):
        cargo = value.get("cargo")
        seat = value.get("seat")
        journey = value.get("journey")
        cargo_num = journey.train.cargo_num
        places_in_cargo = journey.train.places_in_cargo
        Ticket.validate_seat(seat, places_in_cargo)
        Ticket.validate_cargo_num(cargo, cargo_num)
        return value

class JourneyInTicketListSerializer(ModelSerializer):
    train_name = serializers.CharField(source="train.name", read_only=True)
    source = serializers.CharField(source="route.source", read_only=True)
    destination = serializers.CharField(source="route.destination", read_only=True)
    class Meta:
        model = Journey
        fields = ["id", "train_name", "source", "destination", "departure_time", "arrival_time"]


class TicketListSerializer(TicketSerializer):
    journey = JourneyInTicketListSerializer(read_only=True)


class JourneyDetailSerializer(ModelSerializer):
    crew = CrewSerializer(many=True, read_only=True)
    train = TrainSerializer(read_only=True)
    route = RouteSerializer(read_only=True)
    sold_tickets = serializers.IntegerField(read_only=True, source="taken")

    class Meta:
        model = Journey
        fields = ["id", "route", "train", "departure_time", "arrival_time", "crew", "sold_tickets"]


class TicketDetailSerializer(TicketSerializer):
    journey = JourneyDetailSerializer(read_only=True)

class OrderSerializer(ModelSerializer):
    tickets =TicketSerializer(many=True, allow_empty=False)
    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]

    def create(self, validated_data):
        tickets_data = validated_data.pop("tickets")
        with transaction.atomic():
            order = Order.objects.create(**validated_data)
            for ticket in tickets_data:
                try:
                    Ticket.objects.create(order=order, **ticket)
                except Exception as e:
                    raise ValidationError({"tickets": str(e)})
        return order

class OrderListSerializer(OrderSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)

class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)

