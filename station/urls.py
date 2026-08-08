from django.urls import path, include
from rest_framework.routers import DefaultRouter

from station.views import TrainViewSet, JourneyViewSet

app_name = "station"

router = DefaultRouter()
router.register("trains", TrainViewSet)
router.register("journey", JourneyViewSet)
urlpatterns = [
    path("", include(router.urls)),
]