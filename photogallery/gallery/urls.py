from django.conf.urls import url
from django.views.generic.base import RedirectView

from gallery.views import *

app_name = 'gallery'
urlpatterns = [
    url(r'^$', IndexView.as_view(), name='index'),
    url(r'album/(?P<slug>[-\w]+)/$', AlbumView.as_view(), name='album'),
    url(r'album/(?P<slug>[-\w]+)/large$', LargeAlbumView.as_view(), name='album-large'),
    url(r'album/new$', NewAlbumView.as_view(), name='album-new'),
    url(r'album/edit/(?P<slug>[-\w]+)/$', EditAlbumView.as_view(), name='album-edit'),
    url(r'album/scan/(?P<slug>[-\w]+)/$', ScanNewPhotosView.as_view(), name='album-scan'),
    url(r'album/refresh/(?P<slug>[-\w]+)/$', RefreshPhotosView.as_view(), name='album-refresh'),
    url(r'album/download/(?P<slug>[-\w]+)/$', DownloadZipView.as_view(), name='album-download'),
    url(r'setascoverphoto/', UpdateAlbumCoverView.as_view(), name='set-as-cover-photo'),
    url(r'album/delete/(?P<slug>[-\w]+)/$', DeleteAlbumView.as_view(), name='album-delete'),
    url(r'photo/(?P<slug>[-\w]+)/$', PhotoView.as_view(), name='photo'),
    url(r'photo/new$', NewPhotoView.as_view(), name='photo-new'),
    url(r'photo/edit/(?P<slug>[-\w]+)/$', EditPhotoView.as_view(), name='photo-edit'),
    url(r'photo/delete/(?P<slug>[-\w]+)/$', DeletePhotoView.as_view(), name='photo-delete'),
    url(r'photo/massupload', MassUploadView.as_view(), name='photo-massupload'),
    url(r'login/', UserLoginView.as_view(), name='login'),
    url(r'^admin/login/', RedirectView.as_view(url=reverse_lazy("login"))),
    url(r'logout/', LogoutView.as_view(), name='logout'),
]
