from django.urls import path as url
from django.views.generic.base import RedirectView

from gallery.views import *

app_name = 'gallery'
urlpatterns = [
    url('', IndexView.as_view(), name='index'),
    url('album/new', NewAlbumView.as_view(), name='album-new'),
    url('album/<slug:slug>/', AlbumView.as_view(), name='album'),
    url('album/<slug:slug>/large', LargeAlbumView.as_view(), name='album-large'),
    url('album/<slug:slug>/edit/', EditAlbumView.as_view(), name='album-edit'),
    url('album/<slug:slug>/scan/', ScanNewPhotosView.as_view(), name='album-scan'),
    url('album/<slug:slug>/refresh/', RefreshPhotosView.as_view(), name='album-refresh'),
    url('album/<slug:slug>/download/', DownloadZipView.as_view(), name='album-download'),
    url('album/<slug:slug>/delete/', DeleteAlbumView.as_view(), name='album-delete'),
    url('photo/new', NewPhotoView.as_view(), name='photo-new'),
    url('photo/<slug:slug>/', PhotoView.as_view(), name='photo'),
    url('photo/<slug:slug>/edit/', EditPhotoView.as_view(), name='photo-edit'),
    url('photo/<slug:slug>/cover/', SetCoverPhotoView.as_view(), name='photo-setascover'),
    url('photo/<slug:slug>/delete/', DeletePhotoView.as_view(), name='photo-delete'),
    url('upload', MassUploadView.as_view(), name='photo-massupload'),
    url('login/', UserLoginView.as_view(), name='login'),
    url('admin/login/', RedirectView.as_view(url=reverse_lazy('gallery:login'))),
    url('logout/', LogoutView.as_view(), name='logout'),
]
