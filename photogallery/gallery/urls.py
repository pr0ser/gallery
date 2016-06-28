from django.conf.urls import url
from django.views.generic import TemplateView
from . import views

app_name = 'gallery'
urlpatterns = [
    url(r'^$', views.index.as_view(), name='index'),
    url(r'(?P<slug>[-\w]+)/$', views.album.as_view(), name='album'),
]
