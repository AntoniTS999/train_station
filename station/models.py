from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class TrainType(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Train Types"


class Train(models.Model):
    name = models.CharField(max_length=100)
    cargo_num = models.IntegerField() # number of wagons
    places_in_cargo = models.IntegerField() # capacity of each
    train_type = models.ForeignKey(TrainType, on_delete=models.CASCADE, related_name="trains")

    def __str__(self):
        return f"Train:{self.id}, name={self.name}, cargo_num={self.cargo_num}"

    class Meta:
        verbose_name_plural = "Trains"
        ordering = ["cargo_num"]

    @property
    def is_small(self):
        return self.cargo_num <= 5


class Station(models.Model):
    name = models.CharField(max_length=100, unique=True)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)

    def __str__(self):
        return self.name


class Route(models.Model):
    source = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_from")
    destination = models.ForeignKey(Station, on_delete=models.CASCADE, related_name="route_to")
    distance = models.IntegerField()

    def __str__(self):
        return f"The route from: {self.source} to: {self.destination}, distance: {self.distance}"

    class Meta:
        indexes = [models.Index(fields=["source", "destination"])]
        ordering = ["distance"]

class Crew(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Journey(models.Model):
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name="journey")
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="journey")
    departure_time = models.DateTimeField()
    arrival_time = models.DateTimeField()
    crew = models.ManyToManyField(Crew, related_name="journey")

    def __str__(self):
        return f"Journey {self.route} {self.departure_time} {self.arrival_time}"


class Order(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="order")

class Ticket(models.Model):
    cargo = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    journey = models.ForeignKey(Journey, on_delete=models.CASCADE, related_name="tickets")
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="tickets")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["journey", "cargo", "seat"], name="unique_ticket_cargo")
        ]

    def clean(self):
        if not(1 <= self.cargo <= self.journey.train.cargo_num):
            raise ValidationError(f"Cargo must be between 1 to {self.journey.train.cargo_num}")
        if not(1 <= self.seat <= self.journey.train.places_in_cargo):
            raise ValidationError(f"Seat must be between 1 to {self.journey.train.places_in_cargo}")

    def save(self, *args, **kwargs):
        self.full_clean()
        return  super(Ticket, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.journey}- {self.cargo} - {self.seat}"

    @staticmethod
    def validate_cargo_num(cargo, cargo_num):
        if not(1 <= cargo <= cargo_num):
            raise ValidationError(f"Cargo {cargo} is out of range")
    @staticmethod
    def validate_seat(seat, places_in_cargo):
        if not(1 <= seat <= places_in_cargo):
            raise ValidationError(f"Seat {seat} is out of range")






