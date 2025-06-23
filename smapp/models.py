from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

# Create your models here.
class Persona(models.Model):
    """
    Clase base abstracta para reusar campos comunes entre Estudiantes, Profesores, etc.
    No se creará una tabla para esta clase en la base de datos, solo sus herederos.
    """
    TIPOS_DOCUMENTO = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('PA', 'Pasaporte'),
        ('CE', 'Cédula de Extranjería'),
    ]

    primer_nombre = models.CharField(max_length=100)
    segundo_nombre = models.CharField(max_length=100, blank=True, null=True)
    apellido_paterno = models.CharField(max_length=100)
    apellido_materno = models.CharField(max_length=100, blank=True, null=True)
    tipo_documento = models.CharField(max_length=2, choices=TIPOS_DOCUMENTO, default='CC')
    numero_documento = models.CharField(max_length=20, unique=True)
    fecha_nacimiento = models.DateField()
    genero = models.CharField(max_length=1, choices=[('M', 'Masculino'), ('F', 'Femenino'), ('O', 'Otro')])
    direccion = models.CharField(max_length=255, blank=True, null=True)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(unique=True)

    class Meta:
        abstract = True # Indica que esta es una clase abstracta

    def __str__(self):
        return f"{self.primer_nombre} {self.apellido_paterno}"

class Estudiante(Persona):
    """
    Modelo para los estudiantes. Hereda de Persona.
    """
    codigo_estudiante = models.CharField(max_length=20, unique=True)
    fecha_ingreso = models.DateField(auto_now_add=True) # Se establece automáticamente al crear
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.codigo_estudiante} - {self.primer_nombre} {self.apellido_paterno}"

class Profesor(Persona):
    """
    Modelo para los profesores. Hereda de Persona.
    """
    codigo_profesor = models.CharField(max_length=20, unique=True)
    especialidad = models.CharField(max_length=100)
    fecha_contratacion = models.DateField(auto_now_add=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True)
    asignaturas = models.ManyToManyField('Asignatura', related_name='profesores', blank=True)

    def __str__(self):
        return f"{self.codigo_profesor} - {self.primer_nombre} {self.apellido_paterno}"

class Curso(models.Model):
    """
    Modelo para los cursos que se imparten (ej. Matemáticas, Historia, Ciencias).
    """
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    codigo_curso = models.CharField(max_length=10, unique=True)
    profesor_responsable = models.ForeignKey('Profesor', on_delete=models.SET_NULL, null=True, blank=True, related_name='cursos')
    estudiantes = models.ManyToManyField('Estudiante', blank=True, related_name='cursos')
    asignaturas = models.ManyToManyField('Asignatura', blank=True, related_name='cursos')

    def __str__(self):
        return self.nombre

class Asignatura(models.Model):
    """
    Modelo para las asignaturas o materias que componen un curso.
    Un Curso puede tener varias Asignaturas (ej. Matemáticas: Álgebra, Geometría).
    O bien, Asignatura puede ser el nivel más bajo (Matemáticas I, Matemáticas II).
    Si tu escuela tiene "materias" que no son lo mismo que un "curso" general.
    Si no, puedes simplificar y usar solo 'Curso' como la materia a impartir.
    Por simplicidad, vamos a usar 'Asignatura' como la materia que se imparte en un 'Grupo'.
    """
    nombre = models.CharField(max_length=100)
    codigo_asignatura = models.CharField(max_length=10, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    profesor_responsable = models.ForeignKey(
        'Profesor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='asignaturas_responsable'  # <-- Cambia esto
    )

    def __str__(self):
        return self.nombre

class Salon(models.Model):
    """
    Modelo para los salones o aulas donde se imparten las clases.
    """
    numero_salon = models.CharField(max_length=10, unique=True)
    capacidad = models.IntegerField()
    ubicacion = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"Salón {self.numero_salon}"

class PeriodoAcademico(models.Model):
    """
    Modelo para los periodos académicos (ej. Semestre I 2024, Año Escolar 2024-2025).
    """
    nombre = models.CharField(max_length=100, unique=True)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    def __str__(self):
        return self.nombre

class Grupo(models.Model):
    """
    Representa una instancia de una Asignatura impartida en un Periodo Académico por un Profesor
    en un Salón, a un conjunto de Estudiantes.
    """
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    profesor = models.ForeignKey(Profesor, on_delete=models.SET_NULL, null=True, blank=True)
    periodo_academico = models.ForeignKey(PeriodoAcademico, on_delete=models.CASCADE)
    salon = models.ForeignKey(Salon, on_delete=models.SET_NULL, null=True, blank=True)
    estudiantes = models.ManyToManyField(Estudiante, through='Inscripcion') # Relación N:M a través de Inscripcion
    capacidad_maxima = models.IntegerField(default=30)

    def __str__(self):
        return f"{self.asignatura.nombre} - {self.periodo_academico.nombre} ({self.profesor.primer_nombre} {self.profesor.apellido_paterno if self.profesor else 'Sin Profesor'})"

class Inscripcion(models.Model):
    """
    Modelo para registrar la inscripción de un estudiante a un grupo.
    También puede almacenar la calificación final.
    """
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    grupo = models.ForeignKey(Grupo, on_delete=models.CASCADE)
    fecha_inscripcion = models.DateField(auto_now_add=True)
    calificacion_final = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('estudiante', 'grupo') # Un estudiante no puede inscribirse dos veces al mismo grupo

    def __str__(self):
        return f"Inscripción de {self.estudiante} en {self.grupo}"

class Calificacion(models.Model):
    """
    Modelo para registrar calificaciones específicas dentro de un grupo para un estudiante.
    Podría ser para parciales, tareas, exámenes, etc.
    """
    inscripcion = models.ForeignKey(Inscripcion, on_delete=models.CASCADE)
    nombre_evaluacion = models.CharField(max_length=100) # Ej. 'Primer Parcial', 'Tarea 1', etc.
    puntaje = models.DecimalField(max_digits=5, decimal_places=2)
    porcentaje = models.DecimalField(max_digits=5, decimal_places=2, default=0)  # Nuevo campo
    detalle = models.CharField(max_length=255, blank=True, null=True)            # Nuevo campo
    descripcion = models.TextField(blank=True, null=True)                        # Nuevo campo
    fecha_evaluacion = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.inscripcion.estudiante} - {self.inscripcion.grupo.asignatura.nombre} - {self.nombre_evaluacion}: {self.puntaje}"

class EventoCalendario(models.Model):
    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
    ]
    titulo = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True, null=True)
    fecha = models.DateField()
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    creado_en = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.titulo} ({self.fecha})"

class HorarioCurso(models.Model):
    DIAS_SEMANA = [
        ('LU', 'Lunes'),
        ('MA', 'Martes'),
        ('MI', 'Miércoles'),
        ('JU', 'Jueves'),
        ('VI', 'Viernes'),
        ('SA', 'Sábado'),
        ('DO', 'Domingo'),
    ]
    curso = models.ForeignKey(Curso, on_delete=models.CASCADE, related_name='horarios')
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, related_name='horarios', null=True, blank=True)  # <-- AGREGAR ESTA LÍNEA
    dia = models.CharField(max_length=2, choices=DIAS_SEMANA)
    hora_inicio = models.TimeField()
    hora_fin = models.TimeField()

    def __str__(self):
        return f"{self.get_dia_display()} {self.hora_inicio} - {self.hora_fin} ({self.curso.nombre})"

class Perfil(models.Model):
    TIPOS_USUARIO = [
        ('director', 'Director'),
        ('profesor', 'Profesor'),
        ('alumno', 'Alumno'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    tipo_usuario = models.CharField(max_length=10, choices=TIPOS_USUARIO)

    def __str__(self):
        return f"{self.user.username} ({self.get_tipo_usuario_display()})"

class AsistenciaAlumno(models.Model):
    estudiante = models.ForeignKey(Estudiante, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE)
    fecha = models.DateField(default=timezone.now)
    presente = models.BooleanField(default=True)
    observacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('estudiante', 'asignatura', 'fecha')

    def __str__(self):
        return f"{self.estudiante} - {self.asignatura} - {self.fecha} - {'Presente' if self.presente else 'Ausente'}"

class AsistenciaProfesor(models.Model):
    profesor = models.ForeignKey(Profesor, on_delete=models.CASCADE)
    asignatura = models.ForeignKey(Asignatura, on_delete=models.CASCADE, null=True, blank=True)  # <--- Cambia aquí
    fecha = models.DateField(default=timezone.now)
    presente = models.BooleanField(default=True)
    observacion = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        unique_together = ('profesor', 'asignatura', 'fecha')

    def __str__(self):
        return f"{self.profesor} - {self.asignatura} - {self.fecha} - {'Presente' if self.presente else 'Ausente'}"


