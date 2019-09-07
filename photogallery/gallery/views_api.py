from django.db.models import Count, Prefetch
from rest_framework import generics, permissions

from gallery.models import Album
from .serializers import AlbumListSerializer, AlbumSerializer


class AlbumList(generics.ListCreateAPIView):
    queryset = (
        Album.objects
        .all()
        .filter(parent=None)
        .filter(public=True)
        .select_related('album_cover')
        .annotate(photocount=Count('photos'))
    )
    serializer_class = AlbumListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class AlbumDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Album.objects
        .prefetch_related('photos')
        .prefetch_related(
            Prefetch('subalbums', queryset=Album.objects.annotate(photocount=Count('photos')))
        )
        .prefetch_related('subalbums__album_cover')
        .select_related('parent__parent')
    )
    serializer_class = AlbumSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
