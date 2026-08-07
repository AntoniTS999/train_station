from rest_framework.serializers import ModelSerializer

from station.models import Train


class TrainSerializer(ModelSerializer):
    class Meta:
        model = Train
        fields = ["id", "name", "cargo_num", "places_in_cargo", "train_type"]