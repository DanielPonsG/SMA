from django import forms
from .models import Estudiante, Profesor, EventoCalendario

class EstudianteForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = [
            'primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'fecha_nacimiento', 'genero',
            'direccion', 'telefono', 'email', 'codigo_estudiante'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class ProfesorForm(forms.ModelForm):
    class Meta:
        model = Profesor
        fields = [
            'primer_nombre', 'segundo_nombre', 'apellido_paterno', 'apellido_materno',
            'tipo_documento', 'numero_documento', 'fecha_nacimiento', 'genero',
            'direccion', 'telefono', 'email', 'codigo_profesor', 'especialidad'
        ]
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

class EventoCalendarioForm(forms.ModelForm):
    class Meta:
        model = EventoCalendario
        fields = ['titulo', 'descripcion', 'fecha', 'prioridad']
        widgets = {
            'fecha': forms.DateInput(attrs={'type': 'date'}),
        }