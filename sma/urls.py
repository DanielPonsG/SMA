"""
URL configuration for sma project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from django.urls import path
from smapp.views import index_master, index, agregar, modificar, eliminar, listar_estudiantes


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index_master', index_master, name='index_master'),
    path('', index, name='index'),
    # CRUD de Administrador
    path('agregar', agregar, name='agregar'),
    path('modificar', modificar, name='modificar'),
    path('eliminar', eliminar, name='eliminar'),
    path('estudiantes/listar/', listar_estudiantes, name='listar_estudiantes'),

]
