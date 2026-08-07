from django.urls import path, include
from rest_framework.routers import DefaultRouter

from station.views import TrainViewSet

app_name = "station"

router = DefaultRouter()
router.register("trains", TrainViewSet)
urlpatterns = [
    path("", include(router.urls)),
]