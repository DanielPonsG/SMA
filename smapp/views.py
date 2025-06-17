from django.shortcuts import render, get_object_or_404, redirect
from .models import Estudiante, Profesor, EventoCalendario
from .forms import EstudianteForm, ProfesorForm, EventoCalendarioForm
from django.db import models
from django.db.models import Q

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
    tipo = request.GET.get('tipo', 'estudiante')  # Por defecto, estudiante
    mensaje = ""
    if tipo == 'profesor':
        form = ProfesorForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            form.save()
            mensaje = "Profesor agregado correctamente."
            form = ProfesorForm()  # Limpiar formulario
    else:
        form = EstudianteForm(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            form.save()
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
    if request.method == 'POST':
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




