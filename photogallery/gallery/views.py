from django.shortcuts import render
from .models import Album, Photo
from django.views import generic
from django.views.generic.edit  import CreateView, UpdateView, DeleteView
# Create your views here.

class index(generic.ListView):
    template_name = 'index.html'
    context_object_name = 'all_albums'

    def get_queryset(self):
        return Album.objects.all()