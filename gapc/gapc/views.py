# gapc/views.py
from django.shortcuts import render
from django.views.generic import TemplateView
from .models import Asteroid

def home(request):
    return render(request, 'home.html')

class Catalog(TemplateView):
    template_name = 'catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asteroids'] = Asteroid.objects.all()
        return context