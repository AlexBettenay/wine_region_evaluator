from django.urls import path, include

# Separated urls for related API endpoints.
# This is done to keep the code organized and maintainable.
urlpatterns = [
    path("region/", include("api.region.urls")),
    path("analysis/", include("api.analysis.urls")),
]