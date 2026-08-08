from rest_framework.serializers import ModelSerializer

from station.models import Train, Journey, Crew


class TrainSerializer(ModelSerializer):
    class Meta:
        model = Train
        fields = ["id", "name", "cargo_num", "places_in_cargo", "train_type", "is_small"]

class CrewSerializer(ModelSerializer):
    class Meta:
        model = Crew
        fields = ["id", "first_name", "last_name"]

class JourneySerializer(ModelSerializer):
    train = TrainSerializer()
    class Meta:
        model = Journey
        fields = ["id", "route", "train", "departure_time", "arrival_time", "crew"]

class JourneyListSerializer(JourneySerializer):
    crew = CrewSerializer(many=True, read_only=True)

