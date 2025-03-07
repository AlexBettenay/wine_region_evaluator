from django.urls import path
from . import views

urlpatterns = [
    path("", views.RegionView.as_view()),
]