from django.db.models import Count, Prefetch
from rest_framework import generics, permissions

from gallery.models import Album
from .serializers import AlbumListSerializer, AlbumSerializer


class AlbumList(generics.ListCreateAPIView):
    serializer_class = AlbumListSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

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
