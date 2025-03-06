from django.urls import path, include
from . import views

urlpatterns = [
    path("location", include("api.location.urls")),
]