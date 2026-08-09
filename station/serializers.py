from django.db import transaction
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.serializers import ModelSerializer
from rest_framework.validators import UniqueTogetherValidator

from station.models import Train, Journey, Crew, Route, Station, Order, Ticket


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
    class Meta:
        model = Journey
        fields = ["id", "source", "destination", "train", "departure_time", "arrival_time", "crew"]



class JourneyDetailSerializer(JourneySerializer):
    crew = CrewSerializer(many=True, read_only=True)
    train = TrainSerializer(read_only=True)
    route = RouteSerializer(read_only=True)


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

class OrderDetailSerializer(OrderSerializer):
    tickets = TicketDetailSerializer(many=True, read_only=True)

