# gapc/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from .models import Asteroid
from datetime import datetime

def home(request):
    return render(request, 'home.html')

class Catalog(ListView):
    model = Asteroid
    template_name = 'catalog.html'
    context_object_name = 'asteroids'
    ordering = ['-target_discovery_date']

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.GET.get('search', '')

        if query:
            queryset = queryset.filter(
                Q(target_name__icontains=query) | 
                Q(target_description__icontains=query) | 
                Q(target_class__icontains=query)
            )
        
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['search_query'] = self.request.GET.get('search', '')
        return context

    
class AsteroidDetail(TemplateView):
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        asteroid = get_object_or_404(Asteroid, target_name=self.kwargs['target_name'])

        context['asteroid'] = asteroid
        context['observations'] = asteroid.observations.all()
        return context