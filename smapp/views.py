from django.shortcuts import render, get_object_or_404, redirect
from .models import Estudiante, Profesor, EventoCalendario, Curso, HorarioCurso, Asignatura
from .forms import EstudianteForm, ProfesorForm, EventoCalendarioForm, CursoForm, HorarioCursoForm, AsignaturaForm, AsignaturaCompletaForm
from django.db import models
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from .models import Perfil
from django.http import HttpResponseForbidden, JsonResponse
from django.forms import formset_factory
from .forms import SeleccionCursoAlumnoForm, CalificacionForm
from .models import Inscripcion, Grupo, Calificacion, AsistenciaAlumno, AsistenciaProfesor
from datetime import date, datetime, timedelta

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
            # Si tienes campos ManyToMany (como asignaturas), asígnalos después de save()
            if 'asignaturas' in form.cleaned_data:
                profesor.asignaturas.set(form.cleaned_data['asignaturas'])
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
            # Si tienes campos ManyToMany (como cursos), asígnalos después de save()
            if 'cursos' in form.cleaned_data:
                estudiante.cursos.set(form.cleaned_data['cursos'])
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

    if tipo == 'profesor':
        if query:
            resultados = Profesor.objects.filter(
                Q(primer_nombre__icontains=query) |
                Q(apellido_paterno__icontains=query) |
                Q(codigo_profesor__icontains=query) |
                Q(id__iexact=query)  # Permite buscar por ID exacto
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
                Q(primer_nombre__icontains=query) |
                Q(apellido_paterno__icontains=query) |
                Q(codigo_estudiante__icontains=query) |
                Q(id__iexact=query)  # Permite buscar por ID exacto
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

    # Eliminar por ID directo
    if request.method == 'POST' and request.POST.get('eliminar_por_id'):
        id_a_eliminar = request.POST.get('id_a_eliminar')
        if tipo == 'profesor':
            try:
                obj = Profesor.objects.get(id=id_a_eliminar)
                obj.delete()
                mensaje = f"Profesor con ID {id_a_eliminar} eliminado correctamente."
            except Profesor.DoesNotExist:
                mensaje = f"No existe un profesor con ID {id_a_eliminar}."
        else:
            try:
                obj = Estudiante.objects.get(id=id_a_eliminar)
                obj.delete()
                mensaje = f"Estudiante con ID {id_a_eliminar} eliminado correctamente."
            except Estudiante.DoesNotExist:
                mensaje = f"No existe un estudiante con ID {id_a_eliminar}."

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
    filtro_estudiante = request.GET.get('filtro_estudiante', '')
    filtro_profesor = request.GET.get('filtro_profesor', '')

    estudiantes = Estudiante.objects.all()
    profesores = Profesor.objects.all()

    if filtro_estudiante:
        estudiantes = estudiantes.filter(
            models.Q(primer_nombre__icontains=filtro_estudiante) |
            models.Q(apellido_paterno__icontains=filtro_estudiante) |
            models.Q(codigo_estudiante__icontains=filtro_estudiante)
        )
    if filtro_profesor:
        profesores = profesores.filter(
            models.Q(primer_nombre__icontains=filtro_profesor) |
            models.Q(apellido_paterno__icontains=filtro_profesor) |
            models.Q(codigo_profesor__icontains=filtro_profesor)
        )

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
    perfil = getattr(request.user, 'perfil', None)
    tipo_usuario = perfil.tipo_usuario if perfil else None

    cursos_alumno_ids = []
    if tipo_usuario == 'alumno':
        estudiante = getattr(request.user, 'estudiante', None)
        asignaturas = Asignatura.objects.filter(cursos__estudiantes=estudiante).distinct() if estudiante else Asignatura.objects.none()
        if estudiante:
            cursos_alumno_ids = list(estudiante.cursos.values_list('id', flat=True))
    elif tipo_usuario == 'profesor':
        profesor = getattr(request.user, 'profesor', None)
        asignaturas = Asignatura.objects.filter(profesor_responsable=profesor).distinct() if profesor else Asignatura.objects.none()
    else:  # director u otro
        asignaturas = Asignatura.objects.all()

    total_asignaturas = asignaturas.count()
    return render(request, 'listar_asignaturas.html', {
        'asignaturas': asignaturas,
        'total_asignaturas': total_asignaturas,
        'tipo_usuario': tipo_usuario,
        'cursos_alumno_ids': cursos_alumno_ids,
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
            # Crea el usuario
            user = User.objects.create_user(username=username, password=password, email=email)
            # Crea el perfil
            Perfil.objects.create(user=user, tipo_usuario='alumno')
            # Crea el estudiante y lo asocia al usuario
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

from django.contrib.auth.decorators import login_required
from .models import Curso, HorarioCurso

@login_required
def ver_horario_curso(request):
    perfil = getattr(request.user, 'perfil', None)
    es_director = perfil and perfil.tipo_usuario == 'director'
    es_profesor = perfil and perfil.tipo_usuario == 'profesor'
    cursos = Curso.objects.all()
    curso_seleccionado = None
    horarios = []

    if es_director:
        # Director puede seleccionar cualquier curso
        if request.method == "POST":
            curso_id = request.POST.get("curso_id")
            if curso_id:
                curso_seleccionado = Curso.objects.get(id=curso_id)
                horarios = HorarioCurso.objects.filter(curso=curso_seleccionado).select_related('asignatura')
    elif es_profesor:
        # Profesor solo ve sus horarios, asignaturas y cursos
        profesor = getattr(request.user, 'profesor', None)
        # Horarios donde el profesor es responsable de la asignatura
        horarios = HorarioCurso.objects.filter(
            asignatura__profesor_responsable=profesor
        ).select_related('asignatura', 'curso')
    else:
        horarios = []

    context = {
        "cursos": cursos,
        "curso_seleccionado": curso_seleccionado,
        "horarios": horarios,
        "es_director": es_director,
        "es_profesor": es_profesor,
    }
    return render(request, "ver_horario_curso.html", context)

@login_required
def agregar_asignatura_completa(request):
    if not hasattr(request.user, 'perfil') or request.user.perfil.tipo_usuario != 'director':
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")
    mensaje = ""
    errores = []
    if request.method == 'POST':
        form = AsignaturaCompletaForm(request.POST)
        if form.is_valid():
            asignatura = form.save(commit=False)
            if form.cleaned_data['profesor_responsable']:
                asignatura.profesor_responsable = form.cleaned_data['profesor_responsable']
            else:
                asignatura.profesor_responsable = None
            asignatura.save()
            cursos = form.cleaned_data['cursos']
            dias = form.cleaned_data['dias']
            topes = []
            for curso in cursos:
                for dia in dias:
                    hora_inicio = request.POST.get(f"hora_inicio_{dia}")
                    hora_fin = request.POST.get(f"hora_fin_{dia}")
                    # Verificar tope de horario
                    existe_tope = HorarioCurso.objects.filter(
                        curso=curso,
                        dia=dia,
                        # Tope si se solapan los horarios
                        hora_inicio__lt=hora_fin,
                        hora_fin__gt=hora_inicio
                    ).exists()
                    if existe_tope:
                        topes.append(f"Tope en {curso.nombre} el {dict(HorarioCurso.DIAS_SEMANA)[dia]} entre {hora_inicio} y {hora_fin}")
            if topes:
                errores = topes
            else:
                for curso in cursos:
                    curso.asignaturas.add(asignatura)
                    for dia in dias:
                        hora_inicio = request.POST.get(f"hora_inicio_{dia}")
                        hora_fin = request.POST.get(f"hora_fin_{dia}")
                        HorarioCurso.objects.create(
                            curso=curso,
                            asignatura=asignatura,
                            dia=dia,
                            hora_inicio=hora_inicio,
                            hora_fin=hora_fin
                        )
                mensaje = "Asignatura agregada correctamente con horarios y cursos."
                form = AsignaturaCompletaForm()
    else:
        form = AsignaturaCompletaForm()
    return render(request, 'agregar_asignatura_completa.html', {'form': form, 'mensaje': mensaje, 'errores': errores})

@login_required
def ingresar_notas(request):
    mensaje = ""
    curso_id = request.GET.get('curso') or request.POST.get('curso')
    asignatura_id = request.GET.get('asignatura') or request.POST.get('asignatura')
    periodo_id = request.GET.get('periodo') or request.POST.get('periodo')
    SeleccionForm = SeleccionCursoAlumnoForm
    CalificacionFormSet = formset_factory(CalificacionForm, extra=1)

    if request.method == "POST":
        seleccion_form = SeleccionForm(
            request.POST,
            curso_id=curso_id,
            asignatura_id=asignatura_id,
            periodo_id=periodo_id,
            user=request.user  # <-- Agrega esto
        )
        formset = CalificacionFormSet(request.POST)
        if seleccion_form.is_valid() and formset.is_valid():
            curso = seleccion_form.cleaned_data['curso']
            asignatura = seleccion_form.cleaned_data['asignatura']
            alumno = seleccion_form.cleaned_data['alumno']
            periodo = seleccion_form.cleaned_data['periodo']
            # Buscar o crear grupo para la asignatura, curso y periodo académico
            grupo = Grupo.objects.filter(asignatura=asignatura, estudiantes=alumno, periodo_academico=periodo).first()
            if not grupo:
                grupo = Grupo.objects.create(
                    asignatura=asignatura,
                    profesor=asignatura.profesor_responsable,
                    periodo_academico=periodo,
                    capacidad_maxima=30
                )
                grupo.estudiantes.add(alumno)
            inscripcion, created = Inscripcion.objects.get_or_create(grupo=grupo, estudiante=alumno)
            for form in formset:
                if form.cleaned_data:
                    Calificacion.objects.create(
                        inscripcion=inscripcion,
                        nombre_evaluacion=form.cleaned_data['nombre_evaluacion'],
                        puntaje=form.cleaned_data['puntaje'],
                        porcentaje=form.cleaned_data['porcentaje'],
                        detalle=form.cleaned_data['detalle'],
                        descripcion=form.cleaned_data['descripcion'],
                    )
            mensaje = "Notas guardadas correctamente."
            formset = CalificacionFormSet()
    else:
        seleccion_form = SeleccionForm(
            curso_id=curso_id,
            asignatura_id=asignatura_id,
            periodo_id=periodo_id,
            user=request.user  # <-- Agrega esto
        )
        formset = CalificacionFormSet()
    return render(request, "ingresar_notas.html", {
        "seleccion_form": seleccion_form,
        "formset": formset,
        "mensaje": mensaje,
        "curso_id": curso_id,
        "asignatura_id": asignatura_id,
        "periodo_id": periodo_id,
    })

@login_required
def ver_notas_curso(request):
    user = request.user
    perfil = getattr(user, 'perfil', None)
    cursos = Curso.objects.all()  # Mostrar todos los cursos para todos
    curso_id = request.GET.get('curso')
    calificaciones = []
    curso_seleccionado = None

    if curso_id:
        curso_seleccionado = get_object_or_404(Curso, id=curso_id)
        calificaciones = Calificacion.objects.filter(
            inscripcion__grupo__asignatura__cursos=curso_seleccionado
        ).select_related(
            'inscripcion__estudiante',
            'inscripcion__grupo__asignatura'
        ).order_by('inscripcion__estudiante__apellido_paterno', 'inscripcion__grupo__asignatura__nombre')

    return render(request, "ver_notas_curso.html", {
        "cursos": cursos,
        "curso_seleccionado": curso_seleccionado,
        "calificaciones": calificaciones,
    })

@login_required
def api_horarios_cursos(request):
    cursos_ids = request.GET.get("cursos", "")
    ids = [int(i) for i in cursos_ids.split(",") if i.isdigit()]
    horarios = HorarioCurso.objects.filter(curso_id__in=ids).select_related("curso", "asignatura")
    data = [{
        "curso": h.curso.nombre,
        "asignatura": h.asignatura.nombre if h.asignatura else "",
        "dia": h.get_dia_display(),
        "hora_inicio": h.hora_inicio.strftime("%H:%M"),
        "hora_fin": h.hora_fin.strftime("%H:%M"),
    } for h in horarios]
    return JsonResponse(data, safe=False)

@login_required
def editar_nota(request, nota_id):
    nota = get_object_or_404(Calificacion, id=nota_id)
    mensaje = ""
    if request.method == 'POST':
        form = CalificacionForm(request.POST, instance=nota)
        if form.is_valid():
            form.save()
            mensaje = "Nota modificada con éxito"
            return redirect('ver_notas_curso')  # O redirige a la misma vista con el curso seleccionado
    else:
        form = CalificacionForm(instance=nota)
    return render(request, 'editar_nota.html', {'form': form, 'nota': nota, 'mensaje': mensaje})

@login_required
def eliminar_nota(request, nota_id):
    nota = get_object_or_404(Calificacion, id=nota_id)
    if request.method == 'POST':
        nota.delete()
        return redirect('ver_notas_curso')
    return render(request, 'eliminar_nota.html', {'nota': nota})

@login_required
def registrar_asistencia_alumno(request):
    perfil = getattr(request.user, 'perfil', None)
    if perfil and perfil.tipo_usuario == 'profesor':
        # Solo asignaturas del profesor
        asignaturas = Asignatura.objects.filter(profesor_responsable__user=request.user)
        estudiantes = Estudiante.objects.filter(cursos__asignaturas__in=asignaturas).distinct()
    elif perfil and perfil.tipo_usuario == 'director':
        asignaturas = Asignatura.objects.all()
        estudiantes = Estudiante.objects.all()
    else:
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")

    mensaje = ""
    if request.method == 'POST':
        for estudiante_id in request.POST.getlist('estudiante'):
            asignatura_id = request.POST.get('asignatura')
            presente = request.POST.get(f'presente_{estudiante_id}') == 'on'
            fecha = request.POST.get('fecha')
            observacion = request.POST.get(f'observacion_{estudiante_id}', '')
            AsistenciaAlumno.objects.update_or_create(
                estudiante_id=estudiante_id,
                asignatura_id=asignatura_id,
                fecha=fecha,
                defaults={'presente': presente, 'observacion': observacion}
            )
        mensaje = "Asistencia registrada correctamente."
    today = date.today().isoformat()
    return render(request, 'registrar_asistencia_alumno.html', {
        'asignaturas': asignaturas,
        'estudiantes': estudiantes,
        'mensaje': mensaje,
        'today': today,
    })

@login_required
def ver_asistencia_alumno(request):
    perfil = getattr(request.user, 'perfil', None)
    fecha = request.GET.get('fecha', '')
    semana = request.GET.get('semana', '')
    asignatura_id = request.GET.get('asignatura', '')

    if perfil and perfil.tipo_usuario == 'profesor':
        asignaturas = Asignatura.objects.filter(profesor_responsable__user=request.user)
        asistencias = AsistenciaAlumno.objects.filter(asignatura__in=asignaturas)
    elif perfil and perfil.tipo_usuario == 'director':
        asignaturas = Asignatura.objects.all()
        asistencias = AsistenciaAlumno.objects.all()
    else:
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")

    # Filtrar por asignatura si se selecciona
    if asignatura_id:
        asistencias = asistencias.filter(asignatura_id=asignatura_id)

    # Filtrar por fecha exacta
    if fecha:
        asistencias = asistencias.filter(fecha=fecha)

    # Filtrar por semana (YYYY-Www formato ISO)
    if semana:
        try:
            year, week = map(int, semana.split('-W'))
            first_day = datetime.strptime(f'{year}-W{week}-1', "%Y-W%W-%w").date()
            last_day = first_day + timedelta(days=6)
            asistencias = asistencias.filter(fecha__range=[first_day, last_day])
        except Exception:
            pass

    return render(request, 'ver_asistencia_alumno.html', {
        'asistencias': asistencias,
        'asignaturas': asignaturas,
        'fecha': fecha,
        'semana': semana,
        'asignatura_id': asignatura_id,
    })

@login_required
def registrar_asistencia_profesor(request):
    perfil = getattr(request.user, 'perfil', None)
    if perfil and perfil.tipo_usuario == 'director':
        profesores = Profesor.objects.all()
        asignaturas = Asignatura.objects.all()
    else:
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")

    mensaje = ""
    if request.method == 'POST':
        for profesor_id in request.POST.getlist('profesor'):
            asignatura_id = request.POST.get('asignatura')
            presente = request.POST.get(f'presente_{profesor_id}') == 'on'
            fecha = request.POST.get('fecha')
            observacion = request.POST.get(f'observacion_{profesor_id}', '')
            AsistenciaProfesor.objects.update_or_create(
                profesor_id=profesor_id,
                asignatura_id=asignatura_id,
                fecha=fecha,
                defaults={'presente': presente, 'observacion': observacion}
            )
        mensaje = "Asistencia de profesor registrada correctamente."
    today = date.today().isoformat()
    return render(request, 'registrar_asistencia_profesor.html', {
        'asignaturas': asignaturas,
        'profesores': profesores,
        'mensaje': mensaje,
        'today': today,
    })

@login_required
def ver_asistencia_profesor(request):
    perfil = getattr(request.user, 'perfil', None)
    fecha = request.GET.get('fecha', '')
    semana = request.GET.get('semana', '')
    year = request.GET.get('year', '')

    if perfil and perfil.tipo_usuario == 'director':
        asistencias = AsistenciaProfesor.objects.all()
    elif perfil and perfil.tipo_usuario == 'profesor':
        asistencias = AsistenciaProfesor.objects.filter(profesor__user=request.user)
    else:
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")

    # Filtrar por fecha exacta
    if fecha:
        asistencias = asistencias.filter(fecha=fecha)

    # Filtrar por semana (YYYY-Www formato ISO)
    if semana:
        try:
            year_w, week = semana.split('-W')
            year_w = int(year_w)
            week = int(week)
            first_day = datetime.strptime(f'{year_w}-W{week}-1', "%Y-W%W-%w").date()
            last_day = first_day + timedelta(days=6)
            asistencias = asistencias.filter(fecha__range=[first_day, last_day])
        except Exception:
            pass

    # Filtrar por año
    if year:
        asistencias = asistencias.filter(fecha__year=year)

    return render(request, 'ver_asistencia_profesor.html', {
        'asistencias': asistencias,
        'fecha': fecha,
        'semana': semana,
        'year': year,
    })

from .forms import AsistenciaAlumnoForm

@login_required
def editar_asistencia_alumno(request, asistencia_id):
    asistencia = get_object_or_404(AsistenciaAlumno, id=asistencia_id)
    mensaje = ""
    if request.method == 'POST':
        form = AsistenciaAlumnoForm(request.POST, instance=asistencia)
        if form.is_valid():
            form.save()
            mensaje = "Asistencia modificada con éxito."
            return redirect('ver_asistencia_alumno')
    else:
        form = AsistenciaAlumnoForm(instance=asistencia)
    return render(request, 'editar_asistencia_alumno.html', {
        'form': form,
        'asistencia': asistencia,
        'mensaje': mensaje,
    })

from django.shortcuts import render, get_object_or_404, redirect
from .forms import AsistenciaProfesorForm
from .models import AsistenciaProfesor
from django.contrib.auth.decorators import login_required

@login_required
def editar_asistencia_profesor(request, asistencia_id):
    asistencia = get_object_or_404(AsistenciaProfesor, id=asistencia_id)
    mensaje = ""
    if request.method == 'POST':
        form = AsistenciaProfesorForm(request.POST, instance=asistencia)
        if form.is_valid():
            form.save()
            mensaje = "Asistencia modificada con éxito."
            return redirect('ver_asistencia_profesor')
    else:
        form = AsistenciaProfesorForm(instance=asistencia)
    return render(request, 'editar_asistencia_profesores.html', {
        'form': form,
        'asistencia': asistencia,
        'mensaje': mensaje,
    })

from .forms import HorarioCursoForm

@login_required
def agregar_horario(request, curso_id):
    if not hasattr(request.user, 'perfil') or request.user.perfil.tipo_usuario != 'director':
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")
    curso = get_object_or_404(Curso, id=curso_id)
    mensaje = ""
    if request.method == 'POST':
        form = HorarioCursoForm(request.POST)
        if form.is_valid():
            horario = form.save(commit=False)
            horario.curso = curso
            horario.save()
            mensaje = "Horario agregado correctamente."
            return redirect('ver_horario_curso')
    else:
        form = HorarioCursoForm()
    return render(request, 'agregar_horario.html', {'form': form, 'curso': curso, 'mensaje': mensaje})

@login_required
def editar_horario(request, horario_id):
    if not hasattr(request.user, 'perfil') or request.user.perfil.tipo_usuario != 'director':
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")
    horario = get_object_or_404(HorarioCurso, id=horario_id)
    mensaje = ""
    if request.method == 'POST':
        form = HorarioCursoForm(request.POST, instance=horario)
        if form.is_valid():
            form.save()
            mensaje = "Horario modificado correctamente."
            return redirect('ver_horario_curso')
    else:
        form = HorarioCursoForm(instance=horario)
    return render(request, 'editar_horario.html', {'form': form, 'horario': horario, 'mensaje': mensaje})

@login_required
def eliminar_horario(request, horario_id):
    if not hasattr(request.user, 'perfil') or request.user.perfil.tipo_usuario != 'director':
        return HttpResponseForbidden("No tienes permiso para acceder aquí.")
    horario = get_object_or_404(HorarioCurso, id=horario_id)
    if request.method == 'POST':
        horario.delete()
        return redirect('ver_horario_curso')
    return render(request, 'eliminar_horario.html', {'horario': horario})




