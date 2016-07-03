from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

app_name = 'gallery'
urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'album/(?P<slug>[-\w]+)/$', views.AlbumView.as_view(), name='album'),
    url(r'^photo/(?P<slug>[-\w]+)/$', views.PhotoView.as_view(), name='photo'),
    url(r'^login/', views.LoginView.as_view(), name='login'),
    url(r'^logout/', views.LogoutView.as_view(), name='logout'),
]
