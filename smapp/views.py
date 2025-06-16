from django.shortcuts import render

# Create your views here.
# Vista de la página de inicio del maestro
def index_master(request):
    """
    Render the master index page.
    """
    return render(request, 'index_master.html')
# Vista de la página de inicio del alumno
def index(request):
    """
    Render the index page.
    """
    return render(request, 'index.html')


