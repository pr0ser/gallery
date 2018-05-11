import logging
import os
from urllib import parse

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.contrib.postgres.search import SearchRank, SearchVector
from django.db.models import Count, Q
from django.http import HttpResponseForbidden, JsonResponse, StreamingHttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils.crypto import get_random_string
from django.utils.http import is_safe_url
from django.utils.translation import ugettext_lazy as _
from django.views.generic import ListView, DetailView, View
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from zipstream import ZipFile, ZIP_STORED

from gallery.forms import *
from gallery.models import Album, Photo
from gallery.tasks import async_save_photo, update_album_localities
from gallery.utils import PartialQuery

log = logging.getLogger(__name__)


class IndexView(ListView):
    template_name = 'index.html'
    context_object_name = 'albums'

    def get_queryset(self):
        user = self.request.user
        if user.is_authenticated:
            return (
                Album.objects
                .all()
                .filter(parent=None)
                .select_related('album_cover')
                .annotate(photocount=Count('photos'))
            )
        else:
            return (
                Album.objects
                .all()
                .filter(parent=None)
                .filter(public=True)
                .select_related('album_cover')
                .annotate(photocount=Count('photos'))
            )


class AlbumView(ListView):
    template_name = 'album.html'
    context_object_name = 'photos'
    paginate_by = 40

    def get_queryset(self):
        album = get_object_or_404(Album, directory=self.kwargs['slug'])
        queryset = (
            Photo.objects
            .filter(album_id=album.id)
            .filter(ready=True)
            .order_by(album.sort_order)
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(AlbumView, self).get_context_data(**kwargs)
        album = Album.objects.get(directory=self.kwargs['slug'])
        context['album'] = album
        user = self.request.user
        if user.is_authenticated:
            context['sub_albums'] = (
                Album.objects
                .filter(parent=album.id)
                .select_related('album_cover')
                .annotate(photocount=Count('photos'))
            )
        else:
            context['sub_albums'] = (
                Album.objects
                .filter(parent=album.id)
                .filter(public=True)
                .select_related('album_cover')
                .annotate(photocount=Count('photos'))
            )
        return context


class LargeAlbumView(ListView):
    template_name = 'album-large.html'
    context_object_name = 'photos'
    paginate_by = 10

    def get_queryset(self):
        album = get_object_or_404(Album, directory=self.kwargs['slug'])
        queryset = (
            Photo.objects
            .filter(album_id=album.id)
            .filter(ready=True)
            .order_by(album.sort_order)
        )
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LargeAlbumView, self).get_context_data(**kwargs)
        album = Album.objects.get(directory=self.kwargs['slug'])
        context['album'] = album
        return context


class NewAlbumView(LoginRequiredMixin, CreateView):
    form_class = NewAlbumForm
    template_name = 'album-new.html'

    def get_initial(self):
        initial = super(NewAlbumView, self).get_initial()
        initial['parent'] = self.request.GET.get('parent')
        return initial


class EditAlbumView(LoginRequiredMixin, UpdateView):
    model = Album
    form_class = EditAlbumForm
    slug_field = 'directory'
    template_name = 'album-edit.html'


class DeleteAlbumView(LoginRequiredMixin, DeleteView):
    model = Album
    slug_field = 'directory'
    success_url = reverse_lazy('gallery:index')


class DownloadZipView(View):
    def get(self, request, *args, **kwargs):
        album = get_object_or_404(Album, directory=kwargs.get('slug'))
        if not album.downloadable:
            return HttpResponseForbidden()
        photos = (
            Photo.objects
            .filter(album_id=album.id)
            .filter(ready=True)
            .values_list('image', flat=True)
            .iterator()
        )
        file = ZipFile(mode='w', compression=ZIP_STORED)
        os.chdir(settings.MEDIA_ROOT)
        for photo in photos:
            file.write(photo, os.path.basename(photo))
        response = StreamingHttpResponse(file, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename={album.directory}.zip'
        return response


class PhotoView(DetailView):
    model = Photo
    slug_field = 'slug'
    template_name = 'photo.html'
    context_object_name = 'photo'
    queryset = Photo.objects.select_related('album', 'exifdata')


class PhotoMapView(LoginRequiredMixin, DetailView):
    model = Photo
    slug_field = 'slug'
    template_name = 'photo-map.html'
    context_object_name = 'photo'
    queryset = Photo.objects.select_related('album', 'exifdata')

    def get_context_data(self, **kwargs):
        context = super(PhotoMapView, self).get_context_data(**kwargs)
        api_key = os.environ['MAPS_API_KEY']
        context['api_key'] = api_key
        return context


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


class SetCoverPhotoView(LoginRequiredMixin, FormView):
    form_class = AlbumCoverPhotoForm
    template_name = 'photo-cover.html'
    success_url = reverse_lazy('gallery:index')

    def form_valid(self, form):
        photo = self.kwargs.get('slug')
        form.update_album_cover(photo)
        return super(SetCoverPhotoView, self).form_valid(form)

    def get_initial(self):
        initial = super(SetCoverPhotoView, self).get_initial()
        initial['album'] = self.request.GET.get('album_id')
        return initial

    def get_context_data(self, **kwargs):
        context = super(SetCoverPhotoView, self).get_context_data(**kwargs)
        context['photo'] = Photo.objects.get(slug=self.kwargs.get('slug'))
        return context


class MassUploadView(LoginRequiredMixin, FormView):
    form_class = MassUploadForm
    template_name = 'photo-massupload.html'

    def post(self, request, *args, **kwargs):
        form = self.get_form(self.get_form_class())
        files = request.FILES.getlist('image')
        if form.is_valid():
            album = Album.objects.get(pk=form.instance.album.id)
            for file in files:
                title = path.splitext(file.name)[0]
                instance = Photo(
                    title=title,
                    album_id=form.instance.album.id,
                    ready=False,
                    image=file)
                instance.save()
            return JsonResponse({
                'message': 'OK',
                'successUrl': album.get_absolute_url()
            })
        else:
            return JsonResponse({'errors': dict(form.errors.items())}, status=400)

    def get_initial(self):
        initial = super(MassUploadView, self).get_initial()
        initial['album'] = self.request.GET.get('album_id')
        return initial


class ScanNewPhotosView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        album = get_object_or_404(Album, directory=kwargs.get('slug'))
        new_photos, errors = album.scan_new_photos()
        if new_photos == 0:
            messages.info(request, _('No new photos found in the album directory.'))
        if errors:
            messages.error(request, errors)
        return redirect('gallery:album', slug=album.directory)


class InProgressView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        album = get_object_or_404(Album, directory=kwargs.get('slug'))
        post_processing = Photo.objects.filter(album=album.id).filter(ready=False).count()
        updating = album.pending_updates
        data = {
            'post_processing': post_processing,
            'updating': updating
        }
        return JsonResponse(data)


class UpdatePhotosView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        album = get_object_or_404(Album, directory=kwargs.get('slug'))
        async_save_photo.delay(album.id)
        return redirect('gallery:album', slug=album.directory)


class UpdateAlbumLocalityView(LoginRequiredMixin, View):
    def get(self, request, *args, **kwargs):
        album = get_object_or_404(Album, directory=kwargs.get('slug'))
        update_album_localities.delay(album.id)
        messages.info(
            request, _('Geocoding information will be updated '
                       'on the background. It might take a while.'))
        return redirect('gallery:album', slug=album.directory)


class EditExifDataView(LoginRequiredMixin, UpdateView):
    model = ExifData
    form_class = EditExifDataForm
    template_name = 'exif-edit.html'
    pk_url_kwarg = 'photo_id'

    def form_valid(self, form):
        if form.instance.latitude and form.instance.longitude:
            form.instance.has_location = True
        else:
            form.instance.has_location = False
        return super(EditExifDataView, self).form_valid(form)


class SearchView(ListView):
    template_name = 'search.html'
    context_object_name = 'results'
    paginate_by = 40

    def get_queryset(self):
        vector = (
                SearchVector('title', weight='A') +
                SearchVector('description', weight='A') +
                SearchVector('album__title', weight='B') +
                SearchVector('album__description', weight='B') +
                SearchVector('exifdata__locality', weight='C') +
                SearchVector('exifdata__country', weight='C') +
                SearchVector('exifdata__make', weight='D') +
                SearchVector('exifdata__model', weight='D') +
                SearchVector('exifdata__lens', weight='D')
        )
        user = self.request.user
        query = self.request.GET.get('q')
        if query:
            if user.is_authenticated:
                return (
                    Photo.objects
                    .annotate(rank=SearchRank(vector, PartialQuery(query)))
                    .filter(rank__gte=0.01)
                    .order_by('-rank')
                )
            else:
                return (
                    Photo.objects
                    .annotate(rank=SearchRank(vector, PartialQuery(query)))
                    .filter(rank__gte=0.01)
                    .filter(album__public=True)
                    .filter(Q(album__parent__public=True) | Q(album__parent__public__isnull=True))
                    .order_by('-rank')
                )
        else:
            return Photo.objects.none()


class SearchAPIView(View):
    def get(self, request, *args, **kwargs):
        query = self.request.GET.get('q')
        if not query:
            return JsonResponse({'results': []})

        vector = (
            SearchVector('title', weight='A') +
            SearchVector('description', weight='A') +
            SearchVector('album__title', weight='B') +
            SearchVector('album__description', weight='B') +
            SearchVector('exifdata__locality', weight='C') +
            SearchVector('exifdata__country', weight='C') +
            SearchVector('exifdata__make', weight='D') +
            SearchVector('exifdata__model', weight='D') +
            SearchVector('exifdata__lens', weight='D')
        )

        if self.request.user.is_authenticated:
            results = list(
                Photo.objects
                .annotate(rank=SearchRank(vector, PartialQuery(query)))
                .filter(rank__gte=0.01)
                .order_by('-rank')[:6]
                .iterator()
            )
        else:
            results = list(
                Photo.objects
                .annotate(rank=SearchRank(vector, PartialQuery(query)))
                .filter(rank__gte=0.01)
                .filter(album__public=True)
                .filter(Q(album__parent__public=True) | Q(album__parent__public__isnull=True))
                .order_by('-rank')[:6]
                .iterator()
            )

        items = []
        for result in results:
            item = {
                'title': result.title,
                'description': result.description,
                'image': result.thumbnail_img.url,
                'url': result.get_absolute_url()
            }
            items.append(item)

        action = {'url': f'/search?q={parse.quote_plus(query)}', 'text': _('Show all')}
        return JsonResponse({'results': items, 'action': action})


class UserLoginView(LoginView):
    template_name = 'login.html'


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('gallery:index')
