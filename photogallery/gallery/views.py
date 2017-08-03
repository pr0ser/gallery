from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import get_object_or_404, redirect
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView

from gallery.forms import *
from gallery.models import Album, Photo, scan_new_photos, async_save_photo


class IndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'albums'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return Album.objects.all().filter(parent=None).select_related('album_cover')
        else:
            return Album.objects.all().filter(parent=None).filter(public=True).select_related('album_cover')


class AlbumView(ListView):
    template_name = 'album.html'
    context_object_name = 'photos'
    paginate_by = 40

    def get_queryset(self):
        album = get_object_or_404(Album, directory=self.kwargs['slug'])
        queryset = (Photo.objects
                    .filter(album_id=album.id)
                    .filter(ready=True)
                    .order_by(album.sort_order))
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AlbumView, self).get_context_data(**kwargs)
        album = Album.objects.get(directory=self.kwargs['slug'])
        context['album'] = album
        user = self.request.user
        if user.is_authenticated:
            context['sub_albums'] = Album.objects.filter(parent=album.id)
        else:
            context['sub_albums'] = Album.objects.filter(parent=album.id).filter(public=True)
        return context


class LargeAlbumView(ListView):
    template_name = 'album-large.html'
    context_object_name = 'photos'
    paginate_by = 10

    def get_queryset(self):
        album = get_object_or_404(Album, directory=self.kwargs['slug'])
        queryset = Photo.objects.filter(album_id=album.id).filter(ready=True).order_by(album.sort_order)
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LargeAlbumView, self).get_context_data(**kwargs)
        album = Album.objects.get(directory=self.kwargs['slug'])
        context['album'] = album
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


class UpdateAlbumCoverView(LoginRequiredMixin, FormView):
    form_class = AlbumCoverPhotoForm
    template_name = 'album-updatecover.html'
    success_url = reverse_lazy('gallery:index')

    def form_valid(self, form):
        photo_id = self.request.POST.get('photo')
        form.update_album_cover(photo_id)
        return super(UpdateAlbumCoverView, self).form_valid(form)

    def get_initial(self):
        initial = super(UpdateAlbumCoverView, self).get_initial()
        initial['photo'] = self.request.GET.get('photo_id')
        initial['album'] = self.request.GET.get('album_id')
        return initial

    def get_context_data(self, **kwargs):
        context = super(UpdateAlbumCoverView, self).get_context_data(**kwargs)
        context['photo'] = Photo.objects.get(pk=self.request.GET.get('photo_id'))
        return context


class PhotoView(DetailView):
    model = Photo
    slug_field = 'slug'
    template_name = 'photo.html'
    context_object_name = 'photo'
    queryset = Photo.objects.select_related('album')


class NewPhotoView(LoginRequiredMixin, CreateView):
    form_class = NewPhotoForm
    template_name = 'photo-new.html'

    def get_initial(self):
        initial = super(NewPhotoView, self).get_initial()
        initial['album'] = self.request.GET.get('album_id')
        return initial


class EditPhotoView(LoginRequiredMixin, UpdateView):
    model = Photo
    form_class = EditPhotoForm
    slug_field = 'slug'
    template_name = 'photo-edit.html'


class DeletePhotoView(LoginRequiredMixin, DeleteView):
    model = Photo
    slug_field = 'slug'
    success_url = reverse_lazy('gallery:index')

    def get_success_url(self):
        next_url = self.request.POST.get('next')
        if is_safe_url(next_url):
            return next_url
        else:
            return super(DeletePhotoView, self).get_success_url()


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
                                 ready=False,
                                 image=file)
                instance.save()
            return redirect('gallery:album', slug=form.instance.album.directory)
        else:
            return self.form_invalid(form)

    def get_initial(self):
        initial = super(MassUploadView, self).get_initial()
        initial['album'] = self.request.GET.get('album_id')
        return initial


class ScanNewPhotosView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        album = get_object_or_404(Album, directory=kwargs.get('slug'))
        new_photos, errors = scan_new_photos(album.id)
        if new_photos == 0:
            messages.info(request, _('No new photos found in the album directory.'))
        if errors:
            messages.error(request, errors)
        return redirect('gallery:album', slug=album.directory)


class RefreshPhotosView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        album = get_object_or_404(Album, directory=kwargs.get('slug'))
        photos = Photo.objects.filter(album_id=album.id).iterator()
        for photo in photos:
            async_save_photo(photo.id)
        messages.info(request, _('Photos will be scanned for changes on the background. It might take a while.'))
        return redirect('gallery:album', slug=album.directory)


class UserLoginView(LoginView):
    template_name = 'login.html'


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('gallery:index')
