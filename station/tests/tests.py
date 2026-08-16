import tempfile
from datetime import timedelta

from PIL import Image
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from station.models import Train, TrainType, Route, Station, Crew, Journey
from station.serializers import TrainSerializer, JourneySerializer

TRAIN_LIST_URL = reverse("station:train-list")
JOURNEY_LIST_URL = reverse("station:journey-list")

class UnauthenticatedTrainApi(APITestCase):
    """Test checking if not authenticated user can get the access to API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(TRAIN_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTrainAPI(APITestCase):
    def create_sample_train(self, **kwargs):
        train_type = TrainType.objects.create(name="Test")
        data = {
            "name": "TestTrain",
            "cargo_num": 2,
            "places_in_cargo": 10,
            "train_type": train_type,
        }
        data.update(kwargs)
        return Train.objects.create(**data)

    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
        )
        self.client.force_authenticate(user=user)

    def test_train_list(self):
        """Test if authenticated user can get train list"""

        train = self.create_sample_train()
        response = self.client.get(TRAIN_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(response.json()["results"][0]["name"], train.name)

    def test_train_detail(self):
        """Test if authenticated user can get train detail"""

        train = self.create_sample_train()
        url = reverse("station:train-detail", args=[train.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json()["name"], train.name)

    def test_train_create_forbidden_if_not_admin_user(self):
        """Test if not admin user can create train"""
        train_type = TrainType.objects.create(name="Test")
        data = {
            "name": "TestTrain",
            "cargo_num": 2,
            "places_in_cargo": 10,
            "train_type": train_type.id,
        }
        response = self.client.post(TRAIN_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(Train.objects.filter(name="TestTrain").exists())


class AdminUserTrainAPI(APITestCase):

    def setUp(self):
        self.client = APIClient()
        admin_user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
            is_staff=True,
        )
        self.client.force_authenticate(user=admin_user)

    def test_create_train_by_admin_user(self):
        """Test if train could be created by admin user"""

        train_type = TrainType.objects.create(name="Test")
        data = {
            "name": "TestTrain",
            "cargo_num": 2,
            "places_in_cargo": 10,
            "train_type": train_type.id,
        }
        response = self.client.post(TRAIN_LIST_URL, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["name"], data["name"])

    def test_update_train(self):
        """Test if train can be updated"""
        train_type = TrainType.objects.create(name="TestType")
        train = Train.objects.create(name="TestTrain", train_type=train_type, cargo_num=2, places_in_cargo=10)
        data_update = {
            "cargo_num": 3,
        }
        url = reverse("station:train-detail", args=[train.id])
        response = self.client.patch(url, data_update)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["cargo_num"], data_update["cargo_num"])

class TrainSerializerTest(APITestCase):
    def create_sample_train(self, **kwargs):
        train_type = TrainType.objects.create(name="Test")
        train = Train.objects.create(name="TestTrain", cargo_num=2, places_in_cargo=12, train_type=train_type)
        return train

    def test_serializer_fields(self):
        """Test if serializer fields are correct"""
        train = self.create_sample_train()
        serializer = TrainSerializer(train)
        self.assertEqual(serializer.data["name"], train.name)
        self.assertEqual(serializer.data["cargo_num"], train.cargo_num)
        self.assertEqual(serializer.data["train_type"], train.train_type.id)

    def test_the_lack_of_fields(self):
        """Test if error appear if fields are not correct"""
        data = {
            "name": "TestTrain",
            "cargo_num": 2,
        }
        serializer = TrainSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn("places_in_cargo", serializer.errors)
        self.assertIn("train_type", serializer.errors)


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


class ImageUploadTest(APITestCase):
    def create_sample_train(self, **kwargs):
        train_type = TrainType.objects.create(name="Test")
        data = {
            "name": "TestTrain",
            "cargo_num": 2,
            "places_in_cargo": 10,
            "train_type": train_type,
        }
        data.update(kwargs)
        return Train.objects.create(**data)

    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
            is_staff=True,
        )
        self.client.force_authenticate(user=user)

    def test_upload_image(self):
        """Test if upload image is working properly"""

        train = self.create_sample_train()
        url = reverse("station:train-upload_image", args=[train.id])
        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp:
            img = Image.new("RGB", (10, 10))
            img.save(tmp, format="JPEG")
            tmp.seek(0)

            response = self.client.post(url, {"image": tmp}, format="multipart")
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertIn("image", response.data)
            train.refresh_from_db()
            self.assertTrue(train.image)

    def tearDown(self):
        for train in Train.objects.all():
            if train.image:
                train.image.delete()


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




