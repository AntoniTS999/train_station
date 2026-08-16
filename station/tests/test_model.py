from datetime import timedelta

from django.utils import timezone

from rest_framework.test import APITestCase

from station.models import Train, TrainType, Route, Station, Crew, Journey


class ModelTests(APITestCase):
    """Tests check if models str return data correctly"""

    def test_train_type_str(self):
        train_type = TrainType.objects.create(name="TestTrainType")
        self.assertEqual(str(train_type), train_type.name)

    def test_crew_str(self):
        crew = Crew.objects.create(first_name="FirstName", last_name="LastName")
        self.assertEqual(str(crew), f"{crew.first_name} {crew.last_name}")

    def test_journey_str(self):
        train_type = TrainType.objects.create(name="TestType")
        train = Train.objects.create(name="TestTrain", cargo_num=2, places_in_cargo=10, train_type=train_type)
        station_source = Station.objects.create(name="Station A")
        station_destination = Station.objects.create(name="Station B")
        route = Route.objects.create(source=station_source, destination=station_destination, distance=10)
        departure_time = timezone.now()
        arrival_time = timezone.now() + timedelta(hours=1)
        journey = Journey.objects.create(
            route=route,
            departure_time=departure_time,
            arrival_time=arrival_time,
            train=train,
        )
        self.assertEqual(str(journey), f"Journey {journey.route} {journey.departure_time} {journey.arrival_time}")