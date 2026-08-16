from datetime import timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from station.models import Train, TrainType, Route, Station, Journey
from station.serializers import JourneySerializer


JOURNEY_LIST_URL = reverse("station:journey-list")


class JourneySerializerTest(APITestCase):
    def setUp(self):
        self.train_type = TrainType.objects.create(name="TestType")
        self.train = Train.objects.create(name="TestTrain", cargo_num=2, places_in_cargo=10, train_type=self.train_type)
        self.station_source = Station.objects.create(name="Station A")
        self.station_destination = Station.objects.create(name="Station B")
        self.route = Route.objects.create(source=self.station_source, destination=self.station_destination, distance=10)
        self.departure_time = timezone.now()
        self.arrival_time = timezone.now() + timedelta(hours=1)

    def test_journey_serializer_available_field_is_read_only(self):
        """Test if read-only field is not available to serializer"""
        data = {
            "route": self.route.id,
            "train": self.train.id,
            "departure_time": self.departure_time,
            "arrival_time": self.arrival_time,
            "available": 999,
        }
        serializer = JourneySerializer(data=data)
        serializer.is_valid()
        self.assertNotIn("available", serializer.validated_data)


class FilteringTestCase(APITestCase):
    def create_sample_journey(self, **kwargs):
        if "train" not in kwargs:
            train_type = TrainType.objects.create(name="TestType")
            kwargs["train"] = Train.objects.create(name="TestTrain", cargo_num=2, places_in_cargo=10, train_type=train_type)
        if "route" not in kwargs:
            station_start = Station.objects.create(name="Station Start")
            station_end = Station.objects.create(name="Station End")
            kwargs["route"] = Route.objects.create(source=station_start, destination=station_end, distance=10)
        departure_time = timezone.now()
        arrival_time = timezone.now() + timedelta(hours=1)
        load_data = {
            "departure_time": departure_time,
            "arrival_time": arrival_time,
        }
        load_data.update(kwargs)
        return Journey.objects.create(**load_data)

    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
        )
        self.client.force_authenticate(user=user)

    def test_filter_journey(self):
        train_type_filter = TrainType.objects.create(name="TrainTypeFilter")
        train_filter = Train.objects.create(name="TestFilter", cargo_num=2, places_in_cargo=10, train_type=train_type_filter)
        journey_train_type_filter = self.create_sample_journey(train=train_filter)

        station_start_filter = Station.objects.create(name="Start Filtering")
        station_end_filter = Station.objects.create(name="End Filtering")
        route_filter = Route.objects.create(source=station_start_filter, destination=station_end_filter, distance=10)
        departure_date_filter = timezone.now() + timedelta(days=3)
        journey_stations_filter = self.create_sample_journey(route=route_filter, departure_time=departure_date_filter)

        filtering_params_train_type = {
            "train": train_type_filter.name,
        }
        filtering_params_stations = {
            "source": station_start_filter.name,
            "destination": station_end_filter.name,
        }
        filtering_params_date = {
            "date": departure_date_filter.date().isoformat(),
        }


        response = self.client.get(JOURNEY_LIST_URL, filtering_params_train_type)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(response.json()["results"][0]["id"], journey_train_type_filter.id)

        response = self.client.get(JOURNEY_LIST_URL, filtering_params_stations)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(response.json()["results"][0]["id"], journey_stations_filter.id)

        response = self.client.get(JOURNEY_LIST_URL, filtering_params_date)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(response.json()["results"][0]["id"], journey_stations_filter.id)





