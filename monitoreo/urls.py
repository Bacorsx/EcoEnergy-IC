"""
URL configuration for monitoreo project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # Panel de administración
    path("admin/", admin.site.urls),

    # App usuarios (registro, login, logout, perfil)
    path("usuarios/", include("usuarios.urls")),

    # App dispositivos (CRUD principal)
    path("dispositivos/", include("dispositivos.urls")),

    # Ruta raíz → lista de dispositivos
    path("", include("dispositivos.urls")),
]