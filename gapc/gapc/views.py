# gapc/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView
from .models import Asteroid

def home(request):
    return render(request, 'home.html')

class Catalog(TemplateView):
    template_name = 'catalog.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['asteroids'] = Asteroid.objects.all().order_by('-target_discovery_date')
        return context
    
class AsteroidDetail(TemplateView):
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Retrieve the asteroid by its target_name instead of pk
        context['asteroid'] = get_object_or_404(Asteroid, target_name=self.kwargs['target_name'])
        return context