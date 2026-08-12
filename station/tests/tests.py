from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase, APIClient


TRAIN_LIST_URL = reverse("station:train-list")

class UnauthenticatedTrainApi(APITestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        response = self.client.get(TRAIN_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedUserTrainAPI(APITestCase):






