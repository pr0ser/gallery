from django.shortcuts import render, redirect
from django.http import HttpResponseRedirect, HttpResponse
from .models import Album, Photo
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from .forms import NewAlbumForm, EditAlbumForm


class IndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'albums'

    def get_queryset(self):
        return Album.objects.all().filter(parent=None)


class AlbumView(DetailView):
    model = Album
    slug_field = 'directory'
    template_name = 'album.html'
    context_object_name = 'album'


class NewAlbumView(LoginRequiredMixin, CreateView):
    form_class = NewAlbumForm
    template_name = 'album-new.html'


class EditAlbumView(LoginRequiredMixin, UpdateView):
    model = Album
    form_class = EditAlbumForm
    slug_field = 'directory'
    template_name = 'album-edit.html'


class DeleteAlbumView(LoginRequiredMixin, DeleteView):
    model = Album
    slug_field = 'directory'
    success_url = reverse_lazy('gallery:index')


class PhotoView(DetailView):
    model = Photo
    slug_field = 'slug'
    template_name = 'photo.html'
    context_object_name = 'photo'


class LoginView(View):
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return redirect('gallery:index')
            else:
                return HttpResponse("Inactive user.")
        else:
            return redirect('gallery:login')

    def get(self, request):
        return render(request, 'login.html')


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('gallery:index')
