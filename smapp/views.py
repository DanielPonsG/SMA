from django.shortcuts import render, get_object_or_404, redirect
from .models import Estudiante, Profesor, EventoCalendario, Curso, HorarioCurso, Asignatura
from .forms import EstudianteForm, ProfesorForm, EventoCalendarioForm, CursoForm, HorarioCursoForm, AsignaturaForm
from django.db import models
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Perfil
from django.http import HttpResponseForbidden

# Create your views here.
# Vista de la página de inicio del maestro
def index_master(request):
    """
    Redirección.
    """
    return render(request, 'index_master.html')
# Vista de la página de inicio del alumno
def index(request):
    """
    Redirección a la página de inicio.
    """
    return render(request, 'index.html')

# Vistas para el CRUD de Administrador
def agregar(request):
    tipo = request.GET.get('tipo', 'estudiante')
    mensaje = ""
    if tipo == 'profesor':
        form = ProfesorForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            # Crear usuario
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username=username, password=password, email=email)
            # Crear perfil
            Perfil.objects.create(user=user, tipo_usuario='profesor')
            # Crear profesor
            profesor = form.save(commit=False)
            profesor.user = user
            profesor.save()
            mensaje = "Profesor agregado correctamente."
            form = ProfesorForm()  # Limpiar formulario
    else:
        form = EstudianteForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            # Crear usuario
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username=username, password=password, email=email)
            # Crear perfil
            Perfil.objects.create(user=user, tipo_usuario='alumno')
            # Crear estudiante
            estudiante = form.save(commit=False)
            estudiante.user = user
            estudiante.save()
            mensaje = "Estudiante agregado correctamente."
            form = EstudianteForm()  # Limpiar formulario
    return render(request, 'agregar.html', {'form': form, 'tipo': tipo, 'mensaje': mensaje})
def modificar(request):
    tipo = request.GET.get('tipo', 'estudiante')
    query = request.GET.get('q', '')
    seleccionado_id = request.GET.get('id')
    mensaje = ""
    form = None
    resultados = []

    # Buscar y mostrar resultados
    if tipo == 'profesor':
        if query:
            resultados = Profesor.objects.filter(
                models.Q(primer_nombre__icontains=query) |
                models.Q(apellido_paterno__icontains=query) |
                models.Q(codigo_profesor__icontains=query)
            )
        else:
            resultados = Profesor.objects.none()
        if seleccionado_id:
            seleccionado = Profesor.objects.get(id=seleccionado_id)
            if request.method == 'POST':
                form = ProfesorForm(request.POST, instance=seleccionado)
                if form.is_valid():
                    form.save()
                    mensaje = "Profesor modificado correctamente."
            else:
                form = ProfesorForm(instance=seleccionado)
    else:
        if query:
            resultados = Estudiante.objects.filter(
                models.Q(primer_nombre__icontains=query) |
                models.Q(apellido_paterno__icontains=query) |
                models.Q(codigo_estudiante__icontains=query)
            )
        else:
            resultados = Estudiante.objects.none()
        if seleccionado_id:
            seleccionado = Estudiante.objects.get(id=seleccionado_id)
            if request.method == 'POST':
                form = EstudianteForm(request.POST, instance=seleccionado)
                if form.is_valid():
                    form.save()
                    mensaje = "Estudiante modificado correctamente."
            else:
                form = EstudianteForm(instance=seleccionado)

    return render(request, 'modificar.html', {
        'tipo': tipo,
        'query': query,
        'resultados': resultados,
        'form': form,
        'seleccionado_id': seleccionado_id,
        'mensaje': mensaje
    })
def eliminar(request):
    tipo = request.GET.get('tipo', 'estudiante')
    query = request.GET.get('q', '')
    seleccionado_id = request.GET.get('id')
    mensaje = ""
    resultados = []
    objeto = None

    # Buscar y mostrar resultados
    if tipo == 'profesor':
        if query:
            resultados = Profesor.objects.filter(
                models.Q(primer_nombre__icontains=query) |
                models.Q(apellido_paterno__icontains=query) |
                models.Q(codigo_profesor__icontains=query)
            )
        else:
            resultados = Profesor.objects.none()
        if seleccionado_id:
            objeto = Profesor.objects.get(id=seleccionado_id)
            if request.method == 'POST':
                objeto.delete()
                mensaje = "Profesor eliminado correctamente."
                objeto = None
    else:
        if query:
            resultados = Estudiante.objects.filter(
                models.Q(primer_nombre__icontains=query) |
                models.Q(apellido_paterno__icontains=query) |
                models.Q(codigo_estudiante__icontains=query)
            )
        else:
            resultados = Estudiante.objects.none()
        if seleccionado_id:
            objeto = Estudiante.objects.get(id=seleccionado_id)
            if request.method == 'POST':
                objeto.delete()
                mensaje = "Estudiante eliminado correctamente."
                objeto = None

    return render(request, 'eliminar.html', {
        'tipo': tipo,
        'query': query,
        'resultados': resultados,
        'objeto': objeto,
        'seleccionado_id': seleccionado_id,
        'mensaje': mensaje
    })

def listar_estudiantes(request):
    """
    Muestra la lista de estudiantes y profesores registrados, y sus conteos.
    """
    estudiantes = Estudiante.objects.all()
    profesores = Profesor.objects.all()
    total_estudiantes = estudiantes.count()
    total_profesores = profesores.count()
    return render(request, 'listar_estudiantes.html', {
        'estudiantes': estudiantes,
        'profesores': profesores,
        'total_estudiantes': total_estudiantes,
        'total_profesores': total_profesores,
    })

@login_required
def calendario(request):
    filtro_fecha = request.GET.get('fecha', '')
    filtro_prioridad = request.GET.get('prioridad', '')
    filtro_titulo = request.GET.get('titulo', '')
    eventos = EventoCalendario.objects.all().order_by('fecha')
    if filtro_fecha:
        eventos = eventos.filter(fecha=filtro_fecha)
    if filtro_prioridad:
        eventos = eventos.filter(prioridad=filtro_prioridad)
    if filtro_titulo:
        eventos = eventos.filter(titulo__icontains=filtro_titulo)
    mensaje = ""
    # Solo director/profesor pueden agregar eventos
    if request.method == 'POST' and hasattr(request.user, 'perfil') and request.user.perfil.tipo_usuario in ['director', 'profesor']:
        form = EventoCalendarioForm(request.POST)
        if form.is_valid():
            form.save()
            mensaje = "Evento agregado correctamente."
            form = EventoCalendarioForm()
    else:
        form = EventoCalendarioForm()
    return render(request, 'calendario.html', {
        'eventos': eventos,
        'form': form,
        'mensaje': mensaje,
        'filtro_fecha': filtro_fecha,
        'filtro_prioridad': filtro_prioridad,
    })

def editar_evento(request, evento_id):
    evento = get_object_or_404(EventoCalendario, id=evento_id)
    mensaje = ""
    if request.method == 'POST':
        form = EventoCalendarioForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            mensaje = "Evento modificado correctamente."
            return redirect('calendario')
    else:
        form = EventoCalendarioForm(instance=evento)
    return render(request, 'editar_evento.html', {
        'form': form,
        'evento': evento,
        'mensaje': mensaje,
    })

def eliminar_evento(request, evento_id):
    evento = get_object_or_404(EventoCalendario, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        return redirect('calendario')
    return render(request, 'eliminar_evento.html', {'evento': evento})

def listar_cursos(request):
    cursos = Curso.objects.all()
    total_cursos = cursos.count()
    return render(request, 'listar_cursos.html', {
        'cursos': cursos,
        'total_cursos': total_cursos,
    })

def agregar_curso(request):
    mensaje = ""
    if request.method == 'POST':
        form = CursoForm(request.POST)
        if form.is_valid():
            form.save()
            mensaje = "Curso agregado correctamente."
            return redirect('listar_cursos')
    else:
        form = CursoForm()
    return render(request, 'agregar_curso.html', {'form': form, 'mensaje': mensaje})

def editar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    mensaje = ""
    if request.method == 'POST':
        form = CursoForm(request.POST, instance=curso)
        if form.is_valid():
            form.save()
            mensaje = "Curso modificado correctamente."
            return redirect('listar_cursos')
    else:
        form = CursoForm(instance=curso)
    return render(request, 'editar_curso.html', {'form': form, 'curso': curso, 'mensaje': mensaje})

def eliminar_curso(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    if request.method == 'POST':
        curso.delete()
        return redirect('listar_cursos')
    return render(request, 'eliminar_curso.html', {'curso': curso})

def gestionar_horarios(request, curso_id):
    curso = get_object_or_404(Curso, id=curso_id)
    horarios = curso.horarios.all()
    mensaje = ""
    if request.method == 'POST':
        form = HorarioCursoForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.curso = curso
            horario.save()
            mensaje = "Horario agregado correctamente."
            return redirect('gestionar_horarios', curso_id=curso.id)
    else:
        form = HorarioCursoForm()
    return render(request, 'gestionar_horarios.html', {
        'curso': curso,
        'horarios': horarios,
        'form': form,
        'mensaje': mensaje
    })

def listar_asignaturas(request):
    if request.user.perfil.tipo_usuario == 'alumno':
        estudiante = getattr(request.user, 'estudiante', None)
        asignaturas = Asignatura.objects.filter(cursos__estudiantes=estudiante).distinct() if estudiante else Asignatura.objects.none()
    else:
        asignaturas = Asignatura.objects.all()
    total_asignaturas = asignaturas.count()
    return render(request, 'listar_asignaturas.html', {
        'asignaturas': asignaturas,
        'total_asignaturas': total_asignaturas,
    })

def agregar_asignatura(request):
    mensaje = ""
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()
            mensaje = "Asignatura agregada correctamente."
            form = AsignaturaForm()
    else:
        form = AsignaturaForm()
    return render(request, 'agregar_asignatura.html', {'form': form, 'mensaje': mensaje})

def editar_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    mensaje = ""
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            mensaje = "Asignatura modificada correctamente."
            return redirect('listar_asignaturas')
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, 'editar_asignatura.html', {'form': form, 'asignatura': asignatura, 'mensaje': mensaje})

def eliminar_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    if request.method == 'POST':
        asignatura.delete()
        return redirect('listar_asignaturas')
    return render(request, 'eliminar_asignatura.html', {'asignatura': asignatura})

def login_view(request):
    mensaje = ""
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('inicio')  # Redirige a la página de inicio para todos
        else:
            mensaje = "Usuario o contraseña incorrectos."
    return render(request, "login.html", {"mensaje": mensaje})

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def inicio(request):
    return render(request, "inicio.html")

def solo_director_profesor(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or request.user.perfil.tipo_usuario not in ['director', 'profesor']:
            return HttpResponseForbidden("No tienes permiso para acceder aquí.")
        return view_func(request, *args, **kwargs)
    return wrapper

@solo_director_profesor
def agregar_evento(request):
    mensaje = ""
    if request.method == 'POST':
        form = EventoCalendarioForm(request.POST)
        if form.is_valid():
            form.save()
            mensaje = "Evento agregado correctamente."
            form = EventoCalendarioForm()
    else:
        form = EventoCalendarioForm()
    return render(request, 'calendario.html', {
        'form': form,
        'mensaje': mensaje,
    })

@solo_director_profesor
def editar_evento(request, evento_id):
    evento = get_object_or_404(EventoCalendario, id=evento_id)
    mensaje = ""
    if request.method == 'POST':
        form = EventoCalendarioForm(request.POST, instance=evento)
        if form.is_valid():
            form.save()
            mensaje = "Evento modificado correctamente."
            return redirect('calendario')
    else:
        form = EventoCalendarioForm(instance=evento)
    return render(request, 'editar_evento.html', {
        'form': form,
        'evento': evento,
        'mensaje': mensaje,
    })

@solo_director_profesor
def eliminar_evento(request, evento_id):
    evento = get_object_or_404(EventoCalendario, id=evento_id)
    if request.method == 'POST':
        evento.delete()
        return redirect('calendario')
    return render(request, 'eliminar_evento.html', {'evento': evento})

@solo_director_profesor
def agregar_asignatura(request):
    mensaje = ""
    if request.method == 'POST':
        form = AsignaturaForm(request.POST)
        if form.is_valid():
            form.save()
            mensaje = "Asignatura agregada correctamente."
            form = AsignaturaForm()
    else:
        form = AsignaturaForm()
    return render(request, 'agregar_asignatura.html', {'form': form, 'mensaje': mensaje})

@solo_director_profesor
def editar_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    mensaje = ""
    if request.method == 'POST':
        form = AsignaturaForm(request.POST, instance=asignatura)
        if form.is_valid():
            form.save()
            mensaje = "Asignatura modificada correctamente."
            return redirect('listar_asignaturas')
    else:
        form = AsignaturaForm(instance=asignatura)
    return render(request, 'editar_asignatura.html', {'form': form, 'asignatura': asignatura, 'mensaje': mensaje})

@solo_director_profesor
def eliminar_asignatura(request, asignatura_id):
    asignatura = get_object_or_404(Asignatura, id=asignatura_id)
    if request.method == 'POST':
        asignatura.delete()
        return redirect('listar_asignaturas')
    return render(request, 'eliminar_asignatura.html', {'asignatura': asignatura})

from django.contrib.auth.decorators import login_required

@login_required
def mis_horarios(request):
    estudiante = getattr(request.user, 'estudiante', None)
    horarios = []
    if estudiante:
        cursos = estudiante.cursos.all()
        for curso in cursos:
            horarios += list(curso.horarios.all())
    return render(request, 'mis_horarios.html', {'horarios': horarios})

@login_required
def mi_curso(request):
    estudiante = getattr(request.user, 'estudiante', None)
    curso = None
    if estudiante:
        cursos = estudiante.cursos.all()
        if cursos.exists():
            curso = cursos.first()
    return render(request, 'mi_curso.html', {'curso': curso})

def agregar_alumno(request):
    mensaje = ""
    if request.method == 'POST':
        form = EstudianteForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username=username, password=password, email=email)
            Perfil.objects.create(user=user, tipo_usuario='alumno')
            estudiante = form.save(commit=False)
            estudiante.user = user
            estudiante.save()
            mensaje = "Alumno creado correctamente."
            form = EstudianteForm()
    else:
        form = EstudianteForm()
    return render(request, 'agregar_alumno.html', {'form': form, 'mensaje': mensaje})

def agregar_profesor(request):
    mensaje = ""
    if request.method == 'POST':
        form = ProfesorForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            user = User.objects.create_user(username=username, password=password, email=email)
            Perfil.objects.create(user=user, tipo_usuario='profesor')
            profesor = form.save(commit=False)
            profesor.user = user
            profesor.save()
            mensaje = "Profesor creado correctamente."
            form = ProfesorForm()
    else:
        form = ProfesorForm()
    return render(request, 'agregar_profesor.html', {'form': form, 'mensaje': mensaje})




