from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path
from django.urls import path as url
from djoser.views import TokenCreateView, TokenDestroyView, UserViewSet
from rest_framework import routers

"""photogallery URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""

router = routers.DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    url('', include('gallery.urls')),
    url('admin/', admin.site.urls),
    url('api/auth/', include('djoser.urls')),
    url('api/auth/login', TokenCreateView.as_view()),
    url('api/auth/logout', TokenDestroyView.as_view()),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    import debug_toolbar
    urlpatterns = [re_path(r'^__debug__/', include(debug_toolbar.urls))] + urlpatterns
