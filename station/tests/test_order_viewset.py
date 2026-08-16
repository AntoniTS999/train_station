from datetime import timedelta
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase, APIClient

from station.models import Train, TrainType, Route, Station, Journey, Order, Ticket
from station.serializers import OrderSerializer

ORDER_LIST_URL = reverse("station:order-list")

class OrderTestAPI(APITestCase):

    def setUp(self):
        self.client = APIClient()
        self.admin_user = get_user_model().objects.create_user(
            email="test@test.com",
            password="password",
            is_staff=True,
        )
        self.client.force_authenticate(user=self.admin_user)

        self.train_type = TrainType.objects.create(name="TestType")
        self.train = Train.objects.create(name="TestTrain", cargo_num=2, places_in_cargo=10, train_type=self.train_type)

        self.station_source = Station.objects.create(name="Station A")
        self.station_destination = Station.objects.create(name="Station B")
        self.route = Route.objects.create(source=self.station_source, destination=self.station_destination, distance=10)

        self.departure_time = timezone.now()
        self.arrival_time = timezone.now() + timedelta(hours=1)

        self.journey = Journey.objects.create(train=self.train, route=self.route, departure_time=self.departure_time,
                                         arrival_time=self.arrival_time)

    def test_create_order(self):
        """Test if order could be created"""

        data = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": self.journey.id,
                }
            ]
        }
        response = self.client.post(ORDER_LIST_URL, data, format="json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_serializer_order(self):
        """Test if order serializer works properly"""
        data = {
            "tickets": [
                {
                    "cargo": 1,
                    "seat": 1,
                    "journey": self.journey.id,
                }
            ]
        }
        serializer = OrderSerializer(data=data)
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data["tickets"][0]["cargo"], data["tickets"][0]["cargo"])

    def test_update_order(self):
        """Test if put method is not allowed"""

        order = Order.objects.create(
            user=self.admin_user
        )

        Ticket.objects.create(
            order=order,
            cargo=1,
            seat=1,
            journey=self.journey,
        )

        data_update = {
            "tickets": [
                {
                    "cargo": 2,
                    "seat": 10,
                    "journey": self.journey.id,
                }
            ]
        }

        url = reverse(
            "station:order-detail",
            args=[order.id]
        )

        response = self.client.patch(
            url,
            data_update,
            format="json",
        )

        self.assertEqual(
            response.status_code,
            status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_delete_order(self):
        """Test if delete method is allowed"""
        order = Order.objects.create(user=self.admin_user)
        Ticket.objects.create(
            order=order,
            cargo=1,
            seat=1,
            journey=self.journey,
        )
        url = reverse("station:order-detail", args=[order.id])
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            Order.objects.filter(id=order.id).exists()
        )