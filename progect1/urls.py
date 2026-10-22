from django.contrib import admin
from django.urls import include, path
from django.conf.urls.i18n import i18n_patterns


urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
]

urlpatterns += i18n_patterns(
    path("admin/", admin.site.urls),
    path("", include("home.urls")),
    path("", include("register.urls")),
    path("", include("login.urls")),
    path("", include("cabinet.urls")),
    path("", include("interesting.urls")),
    path("", include("guest.urls")),
    path("", include("likes.urls")),
)
