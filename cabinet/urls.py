from django.urls import path

from . import views

urlpatterns = [
    path("cabinet/", views.cabinet, name="cabinet"),
    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),
]
