from django.urls import path

from . import views

urlpatterns = [
    path("post/<int:pk>/like/", views.like_toggle, name="like"),
]
