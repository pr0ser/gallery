from logging import getLogger
from os import path

from django.db.models import Count, Prefetch
from rest_framework import generics, permissions
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Album, Photo
from .serializers import AlbumListSerializer, AlbumSerializer, AllAlbumsSerializer

log = getLogger(__name__)


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
        .prefetch_related(
            Prefetch('photos', queryset=Photo.objects.filter(ready=True))
        )
        .prefetch_related(
            Prefetch('subalbums', queryset=Album.objects.order_by('-date').annotate(photocount=Count('photos')))
        )
        .prefetch_related('subalbums__album_cover')
        .select_related('parent__parent')
    )
    serializer_class = AlbumSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


class AllAlbumsList(generics.ListAPIView):
    serializer_class = AlbumListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    pagination_class = None
    queryset = Album.objects.all()


class PhotoUpload(APIView):
    parser_classes = (FormParser, MultiPartParser)
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def post(self, request):
        album = request.data['album']
        files = request.FILES.getlist('files')
        album = Album.objects.get(pk=album)
        accepted_types = ['image/jpeg', 'image/png']
        results = {'newPhotos': 0, 'rejectedPhotos': 0}

        for file in files:
            try:
                if file.content_type in accepted_types:
                    title = path.splitext(file.name)[0]
                    instance = Photo(
                        title=title,
                        album_id=album.id,
                        ready=False,
                        image=file)
                    instance.save()
                    results['newPhotos'] += 1
                else:
                    raise Exception(f'Unsupported file type {file.content_type} in {file.name}')
            except Exception as e:
                log.error(f'Failed to process photo: {file.name} Error: {e}')
                results['rejectedPhotos'] += 1
        if results['newPhotos'] == 0:
            return Response(data=results, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(data=results, status=status.HTTP_201_CREATED)
