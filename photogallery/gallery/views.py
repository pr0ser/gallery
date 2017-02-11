from os import path

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from .forms import *
from .models import Album, Photo


class IndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'albums'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Album.objects.all().filter(parent=None)
        else:
            return Album.objects.all().filter(parent=None).filter(public=True)


class AlbumView(ListView):
    template_name = 'album.html'
    context_object_name = 'photos'
    paginate_by = 40

    def get_queryset(self):
        album = get_object_or_404(Album, directory=self.kwargs['slug'])
        queryset = Photo.objects.filter(album_id=album.id).order_by(album.sort_order)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AlbumView, self).get_context_data(**kwargs)
        context['album'] = Album.objects.get(directory=self.kwargs['slug'])
        return context


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

#class UpdateAlbumCoverView(LoginRequiredMixin, View):
#    def get(self, request, *args, **kwargs):



class PhotoView(DetailView):
    model = Photo
    slug_field = 'slug'
    template_name = 'photo.html'
    context_object_name = 'photo'


class NewPhotoView(LoginRequiredMixin, CreateView):
    form_class = NewPhotoForm
    template_name = 'photo-new.html'


class EditPhotoView(LoginRequiredMixin, UpdateView):
    model = Photo
    form_class = EditPhotoForm
    slug_field = 'slug'
    template_name = 'photo-edit.html'


class DeletePhotoView(LoginRequiredMixin, DeleteView):
    model = Photo
    slug_field = 'slug'
    success_url = reverse_lazy('gallery:index')


class MassUploadView(LoginRequiredMixin, FormView):
    form_class = MassUploadForm
    template_name = 'photo-massupload.html'
    success_url = reverse_lazy('gallery:index')

    def post(self, request, *args, **kwargs):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        files = request.FILES.getlist('image')
        if form.is_valid():
            for file in files:
                instance = Photo(title=path.splitext(file.name)[0],
                                 album_id=form.instance.album.id,
                                 image=file)
                instance.save()
            return redirect('gallery:index')
        else:
            return self.form_invalid(form)


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
