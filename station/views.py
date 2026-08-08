from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from station.models import Train, Journey
from station.serializers import TrainSerializer, JourneySerializer, JourneyListSerializer


class TrainViewSet(ModelViewSet):
    serializer_class = TrainSerializer
    queryset = Train.objects.all()

class JourneyViewSet(ModelViewSet):
    queryset = Journey.objects.all()

    def get_serializer_class(self):
        if self.action in ["list", "retrieve"]:
            return JourneyListSerializer
        else:
            return JourneySerializer
