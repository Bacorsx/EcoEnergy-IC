from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("lista/", views.device_list, name="device_list"),
    path("nuevo/", views.device_create, name="device_create"),
    path("<int:pk>/", views.device_detail, name="device_detail"),
    path("<int:pk>/editar/", views.device_update, name="device_update"),
    path("<int:pk>/eliminar/", views.device_delete, name="device_delete"),
    path("measurements/", views.measurement_list, name="measurement_list"),
    path("alerts/", views.alert_list, name="alert_list"),
    ]