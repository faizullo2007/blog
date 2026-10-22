from django.urls import path

from . import views

urlpatterns = [
    path("user/<str:username>/", views.guest_room, name="guest_room"),
]
