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
from smapp.views import index_master, index, agregar, modificar, eliminar, listar_estudiantes, calendario, editar_evento, eliminar_evento, listar_cursos, agregar_curso, editar_curso, eliminar_curso, gestionar_horarios, listar_asignaturas, agregar_asignatura, editar_asignatura, eliminar_asignatura, login_view, inicio, logout_view, mis_horarios, mi_curso, ver_horario_curso, agregar_asignatura_completa, ingresar_notas, ver_notas_curso


urlpatterns = [
    path('admin/', admin.site.urls),
    path('index_master', index_master, name='index_master'),
    path('login/', login_view, name='login'),
    path('', inicio, name='inicio'),
    # CRUD de Administrador
    path('agregar', agregar, name='agregar'),
    path('modificar', modificar, name='modificar'),
    path('eliminar', eliminar, name='eliminar'),
    path('estudiantes/listar/', listar_estudiantes, name='listar_estudiantes'),
    path('calendario/', calendario, name='calendario'),
    path('calendario/editar/<int:evento_id>/', editar_evento, name='editar_evento'),
    path('calendario/eliminar/<int:evento_id>/', eliminar_evento, name='eliminar_evento'),
    path('cursos/', listar_cursos, name='listar_cursos'),
    path('cursos/agregar/', agregar_curso, name='agregar_curso'),
    path('cursos/editar/<int:curso_id>/', editar_curso, name='editar_curso'),
    path('cursos/eliminar/<int:curso_id>/', eliminar_curso, name='eliminar_curso'),
    path('cursos/<int:curso_id>/horarios/', gestionar_horarios, name='gestionar_horarios'),
    path('asignaturas/', listar_asignaturas, name='listar_asignaturas'),
    path('asignaturas/agregar/', agregar_asignatura, name='agregar_asignatura'),
    path('asignaturas/editar/<int:asignatura_id>/', editar_asignatura, name='editar_asignatura'),
    path('asignaturas/eliminar/<int:asignatura_id>/', eliminar_asignatura, name='eliminar_asignatura'),
    path('logout/', logout_view, name='logout'),
    path('mis-horarios/', mis_horarios, name='mis_horarios'),
    path('mi-curso/', mi_curso, name='mi_curso'),
    path('cursos/ver-horario/', ver_horario_curso, name='ver_horario_curso'),
    path('asignaturas/agregar-completa/', agregar_asignatura_completa, name='agregar_asignatura_completa'),
    path('notas/ingresar/', ingresar_notas, name='ingresar_notas'),
    path('notas/ver/', ver_notas_curso, name='ver_notas_curso'),
]
