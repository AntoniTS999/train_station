from rest_framework.viewsets import ModelViewSet
from station.models import Train, Journey
from station.serializers import TrainSerializer, JourneySerializer, JourneyListSerializer, JourneyDetailSerializer


class TrainViewSet(ModelViewSet):
    serializer_class = TrainSerializer
    queryset = Train.objects.all()


class JourneyViewSet(ModelViewSet):
    queryset = Journey.objects.all()

    def get_serializer_class(self):
        if self.action in ["list"]:
            return JourneyListSerializer
        elif self.action in ["retrieve"]:
            return JourneyDetailSerializer
        else:
            return JourneySerializer

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return Journey.objects.all().select_related("route", "train").prefetch_related("crew")
        else:
            return Journey.objects.all()
