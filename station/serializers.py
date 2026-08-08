from rest_framework import serializers
from rest_framework.serializers import ModelSerializer

from station.models import Train, Journey, Crew, Route, Station, Order


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


class JourneyListSerializer(JourneySerializer):
    train = serializers.SlugRelatedField(many=False, read_only=True, slug_field="name")



class JourneyDetailSerializer(JourneyListSerializer):
    crew = CrewSerializer(many=True, read_only=True)
    train = TrainSerializer(read_only=True)
    route = RouteSerializer(read_only=True)


class OrderSerializer(ModelSerializer):
    class Meta:
        model = Order
        fields = ["id", "created_at", "tickets"]