from django.urls import path as url, include
from django.views.generic.base import RedirectView
from djoser.views import TokenCreateView, TokenDestroyView
from rest_framework import routers

from .views import *
from .views_api import *

router = routers.DefaultRouter()

app_name = 'gallery'
urlpatterns = [
    url('', IndexView.as_view(), name='index'),
    url('album/new', NewAlbumView.as_view(), name='album-new'),
    url('album/<slug:slug>', AlbumView.as_view(), name='album'),
    url('album/<slug:slug>/large', LargeAlbumView.as_view(), name='album-large'),
    url('album/<slug:slug>/edit', EditAlbumView.as_view(), name='album-edit'),
    url('album/<slug:slug>/scan', ScanNewPhotosView.as_view(), name='album-scan'),
    url('album/<slug:slug>/in-progress', InProgressView.as_view(), name='album-in-progress'),
    url('album/<slug:slug>/refresh', UpdatePhotosView.as_view(), name='album-update'),
    url('album/<slug:slug>/download', DownloadZipView.as_view(), name='album-download'),
    url('album/<slug:slug>/delete', DeleteAlbumView.as_view(), name='album-delete'),
    url('photo/new', NewPhotoView.as_view(), name='photo-new'),
    url('photo/<slug:slug>', PhotoView.as_view(), name='photo'),
    url('photo/<slug:slug>/map', PhotoMapView.as_view(), name='photo-map'),
    url('photo/<slug:slug>/edit', EditPhotoView.as_view(), name='photo-edit'),
    url('photo/<slug:slug>/cover', SetCoverPhotoView.as_view(), name='photo-setascover'),
    url('photo/<slug:slug>/delete', DeletePhotoView.as_view(), name='photo-delete'),
    url('exif/<int:photo_id>/edit', EditExifDataView.as_view(), name='exif-edit'),
    url('upload', MassUploadView.as_view(), name='photo-massupload'),
    url('search', SearchView.as_view(), name='search'),
    url('api/search', SearchAPIView.as_view(), name='search-api'),
    url('login/', UserLoginView.as_view(), name='login'),
    url('admin/login/', RedirectView.as_view(url=reverse_lazy('gallery:login'))),
    url('logout', LogoutView.as_view(), name='logout'),

    # DRF API urls
    url('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url('api/auth/login', TokenCreateView.as_view()),
    url('api/auth/logout', TokenDestroyView.as_view()),
    url('api/', include(router.urls)),
    url('api/albums', AlbumList.as_view(), name="album-list"),
    url('api/albums/<int:pk>', AlbumDetail.as_view(), name='album-detail'),
    url('api/upload', PhotoUpload2.as_view(), name="upload")
]
