from rest_framework.viewsets import ModelViewSet
from station.models import Train, Journey, Order, Ticket
from station.serializers import TrainSerializer, JourneySerializer, JourneyListSerializer, JourneyDetailSerializer, \
    OrderSerializer, TicketSerializer, OrderDetailSerializer


class TrainViewSet(ModelViewSet):
    serializer_class = TrainSerializer
    queryset = Train.objects.all()

    def get_queryset(self):
        if self.action in ["list", "retrieve"]:
            return Train.objects.all().select_related("train_type")
        else:
            return Train.objects.all()


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
            return Journey.objects.all().select_related("route", "route__source", "route__destination", "train", "train__train_type").prefetch_related("crew")
        else:
            return Journey.objects.all()


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    http_method_names = ["get", "post", "delete", "head", "options"]

    def get_queryset(self):
        qs = Order.objects.filter(user=self.request.user)
        if self.action in ["list", "retrieve"]:
            return qs.prefetch_related("tickets")
        else:
            return qs.all()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "retrieve":
            return OrderDetailSerializer
        else:
            return OrderSerializer


