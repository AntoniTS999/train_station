from django.contrib import admin
from django.contrib.auth.models import  Group
from station.models import Train, TrainType, Order, Crew, Station, Route, Journey, Ticket

admin.site.register(Train)
admin.site.register(TrainType)
admin.site.register(Crew)
admin.site.register(Station)
admin.site.register(Route)
admin.site.register(Journey)
admin.site.register(Ticket)


class TicketInline(admin.TabularInline):
    model = Ticket
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    inlines = [TicketInline]

admin.site.register(Order, OrderAdmin)

admin.site.unregister(Group)

