# dispositivos/urls.py
from django.urls import path
from . import views

app_name = "dispositivos"

urlpatterns = [
    # Dashboard (HU1)
    path("", views.dashboard, name="dashboard"),

    # Zones
    path("zones/", views.zone_list, name="zone_list"),
    path("zones/<int:pk>/", views.zone_detail, name="zone_detail"),

    # Categories
    path("categories/", views.category_list, name="category_list"),

    # Devices
    path("devices/", views.device_list, name="device_list"),
    path("devices/create/", views.device_create, name="device_create"),
    path("devices/<int:pk>/", views.device_detail, name="device_detail"),
    path("devices/<int:pk>/edit/", views.device_update, name="device_update"),
    path("devices/<int:pk>/delete/", views.device_delete, name="device_delete"),

    # Products
    path("products/", views.product_list, name="product_list"),
    path("products/create/", views.product_create, name="product_create"),
    path("products/<int:pk>/", views.product_detail, name="product_detail"),
    path("products/<int:pk>/edit/", views.product_update, name="product_update"),
    path("products/<int:pk>/delete/", views.product_delete, name="product_delete"),

    # Measurements (tope 50 en la vista)
    path("measurements/", views.measurement_list, name="measurement_list"),

    # Alerts
    path("alerts/", views.alert_list, name="alert_list"),
    path("alerts/<int:pk>/resolve/", views.resolve_event, name="resolve_event"),
]
