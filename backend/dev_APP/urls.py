from django.urls import path
from . import views


urlpatterns = [
    path("health/", views.health, name="health"),
    path("health/live/", views.live, name="health_live"),
    path("health/ready/", views.ready, name="health_ready"),

    path('dashboard/', views.dev_dashboard, name='dev_dashboard'),
    path("logs/", views.dev_logs, name="dev_logs"),
    path("database/", views.dev_database, name="dev_database"),
    path("system/", views.dev_system, name="dev_system"),
]
