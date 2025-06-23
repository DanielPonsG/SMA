from django import forms
from .models import Estudiante, Profesor, EventoCalendario, Curso, HorarioCurso, Asignatura, Inscripcion, Calificacion, Grupo, PeriodoAcademico, AsistenciaAlumno, AsistenciaProfesor

class EstudianteForm(forms.ModelForm):
    username = forms.CharField(label="Nombre de usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Estudiante
        fields = [
            'primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'fecha_nacimiento', 'genero',
            'direccion', 'telefono', 'email', 'codigo_estudiante'
        ]

class ProfesorForm(forms.ModelForm):
    username = forms.CharField(label="Nombre de usuario")
    password = forms.CharField(label="Contraseña", widget=forms.PasswordInput)

    class Meta:
        model = Profesor
        fields = [
            'primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'fecha_nacimiento', 'genero',
            'direccion', 'telefono', 'email', 'codigo_profesor', 'especialidad'
        ]

class EventoCalendarioForm(forms.ModelForm):
    class Meta:
        model = EventoCalendario
        fields = ['titulo', 'descripcion', 'fecha', 'prioridad']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }

class CursoForm(forms.ModelForm):
    class Meta:
        model = Curso
        fields = ['nombre', 'descripcion', 'codigo_curso', 'profesor_responsable', 'estudiantes', 'asignaturas']

class HorarioCursoForm(forms.ModelForm):
    class Meta:
        model = HorarioCurso
        fields = ['dia', 'hora_inicio', 'hora_fin', 'asignatura']
        widgets = {
            'hora_inicio': forms.TimeInput(attrs={'type': 'time'}),
            'hora_fin': forms.TimeInput(attrs={'type': 'time'}),
        }

class AsignaturaForm(forms.ModelForm):
    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo_asignatura', 'descripcion', 'profesor_responsable']

class AsignaturaCompletaForm(forms.ModelForm):
    profesor_responsable = forms.ModelChoiceField(
        queryset=Profesor.objects.all(),
        label="Profesor responsable",
        required=False
    )
    cursos = forms.ModelMultipleChoiceField(
        queryset=Curso.objects.all(),
        label="Cursos",
        required=True
    )
    dias = forms.MultipleChoiceField(
        choices=HorarioCurso.DIAS_SEMANA,
        label="Días",
        widget=forms.CheckboxSelectMultiple,
        required=True
    )

    class Meta:
        model = Asignatura
        fields = ['nombre', 'codigo_asignatura', 'descripcion', 'profesor_responsable', 'cursos', 'dias']

class SeleccionCursoAlumnoForm(forms.Form):
    curso = forms.ModelChoiceField(queryset=Curso.objects.all(), label="Curso")
    asignatura = forms.ModelChoiceField(queryset=Asignatura.objects.none(), label="Asignatura", required=False)
    periodo = forms.ModelChoiceField(
        queryset=PeriodoAcademico.objects.filter(
            nombre__in=["Semestre 1", "Semestre 2"], activo=True
        ),
        label="Periodo académico",
        required=True
    )
    alumno = forms.ModelChoiceField(queryset=Estudiante.objects.none(), label="Alumno", required=False)

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # <-- Agrega esto
        curso_id = kwargs.pop('curso_id', None)
        asignatura_id = kwargs.pop('asignatura_id', None)
        periodo_id = kwargs.pop('periodo_id', None)
        super().__init__(*args, **kwargs)
        if curso_id:
            self.fields['curso'].initial = curso_id
            # Filtra asignaturas por curso y por profesor responsable si es profesor
            if user and hasattr(user, 'perfil') and user.perfil.tipo_usuario == 'profesor':
                profesor = getattr(user, 'profesor', None)
                self.fields['asignatura'].queryset = Asignatura.objects.filter(
                    cursos__id=curso_id,
                    profesor_responsable=profesor
                )
            else:
                self.fields['asignatura'].queryset = Asignatura.objects.filter(cursos__id=curso_id)
            self.fields['alumno'].queryset = Estudiante.objects.filter(cursos__id=curso_id)
        else:
            self.fields['asignatura'].queryset = Asignatura.objects.none()
            self.fields['alumno'].queryset = Estudiante.objects.none()
        if asignatura_id:
            self.fields['asignatura'].initial = asignatura_id
        if periodo_id:
            self.fields['periodo'].initial = periodo_id

class CalificacionForm(forms.ModelForm):
    class Meta:
        model = Calificacion
        fields = ['nombre_evaluacion', 'puntaje', 'porcentaje', 'detalle', 'descripcion']

class AsistenciaAlumnoForm(forms.ModelForm):
    class Meta:
        model = AsistenciaAlumno
        fields = ['presente', 'observacion']

class AsistenciaProfesorForm(forms.ModelForm):
    class Meta:
        model = AsistenciaProfesor
        fields = ['presente', 'observacion']