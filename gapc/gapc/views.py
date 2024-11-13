# gapc/views.py
from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, ListView
from django.db.models import Q
from .models import Asteroid
from datetime import datetime


from django.shortcuts import render
from django.views.generic import TemplateView
from django.db.models import Q
from .models import Asteroid

class Catalog(TemplateView):
    template_name = 'catalog.html'
    context_object_name = 'asteroids'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Retrieve query parameters
        search_query = self.request.GET.get('search', '')
        selected_classification = self.request.GET.get('classification', '')
        order_by_date = self.request.GET.get('order', 'desc')  # Default to descending order

        # Filter asteroids based on search and classification
        queryset = Asteroid.objects.all()
        
        if search_query:
            queryset = queryset.filter(
                Q(target_name__icontains=search_query) | 
                Q(target_description__icontains=search_query)
            )
        
        if selected_classification:
            queryset = queryset.filter(target_class=selected_classification)
        
        # Apply sorting based on the order_by_date option
        if order_by_date == 'asc':
            queryset = queryset.order_by('target_discovery_date')
        else:
            queryset = queryset.order_by('-target_discovery_date')
        
        # Get unique classification choices from the database
        classifications = set(Asteroid.objects.values_list('target_class', flat=True).distinct())
        
        context['asteroids'] = queryset
        context['search_query'] = search_query
        context['selected_classification'] = selected_classification
        context['classifications'] = sorted(classifications)  # Sort alphabetically, optional
        context['order_by_date'] = order_by_date
        return context
    
class AsteroidDetail(TemplateView):
    template_name = 'asteroid_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        asteroid = get_object_or_404(Asteroid, target_name=self.kwargs['target_name'])

        context['asteroid'] = asteroid
        context['observations'] = asteroid.observations.all()
        return context