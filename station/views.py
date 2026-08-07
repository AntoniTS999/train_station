from django.shortcuts import render
from rest_framework.viewsets import ModelViewSet

from station.models import Train
from station.serializers import TrainSerializer


class TrainViewSet(ModelViewSet):
    serializer_class = TrainSerializer
    queryset = Train.objects.all()
