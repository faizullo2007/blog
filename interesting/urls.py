from django.urls import path

from . import views

urlpatterns = [
    path("interesting/", views.interesting, name="interesting"),
]
