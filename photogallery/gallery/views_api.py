from django.db.models import Count, Prefetch
from rest_framework import generics, permissions

from .models import Album
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
                .order_by('-date')
                .select_related('album_cover')
                .annotate(photocount=Count('photos'))
            )
        else:
            return (
                Album.objects
                .all()
                .filter(parent=None)
                .order_by('-date')
                .filter(public=True)
                .select_related('album_cover')
                .annotate(photocount=Count('photos'))
            )


class AlbumDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = (
        Album.objects
        .prefetch_related('photos')
        .prefetch_related(
            Prefetch('subalbums', queryset=Album.objects.order_by('-date').annotate(photocount=Count('photos')))
        )
        .prefetch_related('subalbums__album_cover')
        .select_related('parent__parent')
    )
    serializer_class = AlbumSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)
