from django.conf.urls import url
from django.views.decorators.vary import vary_on_cookie

from . import views

app_name = 'gallery'
urlpatterns = [
    url(r'^$', vary_on_cookie(views.IndexView.as_view()), name='index'),
    url(r'album/(?P<slug>[-\w]+)/$', views.AlbumView.as_view(), name='album'),
    url(r'album/new$', views.NewAlbumView.as_view(), name='album-new'),
    url(r'album/edit/(?P<slug>[-\w]+)/$', views.EditAlbumView.as_view(), name='album-edit'),
    url(r'setascoverphoto/', views.UpdateAlbumCoverView.as_view(), name='set-as-cover-photo'),
    url(r'album/delete/(?P<slug>[-\w]+)/$', views.DeleteAlbumView.as_view(), name='album-delete'),
    url(r'^photo/(?P<slug>[-\w]+)/$', views.PhotoView.as_view(), name='photo'),
    url(r'photo/new$', views.NewPhotoView.as_view(), name='photo-new'),
    url(r'photo/edit/(?P<slug>[-\w]+)/$', views.EditPhotoView.as_view(), name='photo-edit'),
    url(r'photo/delete/(?P<slug>[-\w]+)/$', views.DeletePhotoView.as_view(), name='photo-delete'),
    url(r'photo/massupload', views.MassUploadView.as_view(), name='photo-massupload'),
    url(r'^login/', views.LoginView.as_view(), name='login'),
    url(r'^logout/', views.LogoutView.as_view(), name='logout'),
]
