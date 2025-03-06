from django.urls import path
from . import views

# Separated urls for locations related API endpoints.
# This is done to keep the code organized and maintainable.
# currently only the one base endpoint, but more could be added in the future.
urlpatterns = [
    path("", views.LocationView.as_view()),
]