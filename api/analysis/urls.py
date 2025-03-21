from django.urls import path
from . import views

urlpatterns = [
    path("season", views.WineRegionSeasonAnalysisView.as_view()),
    path("viability", views.WineRegionViabilityAnalysisView.as_view()),
    path("compare_performance", views.WineRegionPerformanceComparisonView.as_view())
]