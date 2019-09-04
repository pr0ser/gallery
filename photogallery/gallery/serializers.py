from rest_framework import serializers

from .models import Album, Photo


class AlbumCoverPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = ['thumbnail_img', 'hidpi_thumbnail_img']


class AlbumListSerializer(serializers.ModelSerializer):
    url = serializers.URLField(source='get_absolute_url', read_only=True)
    photo_count = serializers.SerializerMethodField()
    album_cover = AlbumCoverPhotoSerializer(many=False, read_only=True, allow_null=True)

    class Meta:
        model = Album
        fields = (
            'id',
            'title',
            'date',
            'description',
            'url',
            'photo_count',
            'public',
            'directory',
            'album_cover',
        )

    def get_photo_count(self, obj):
        return obj.photocount


class PhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Photo
        fields = [
            'id',
            'title',
            'slug',
            'date',
            'image',
            'description',
            'preview_img',
            'hidpi_preview_img',
            'thumbnail_img',
            'hidpi_thumbnail_img',
            'ready'
        ]


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True, allow_null=True)
    parent_albums = serializers.SerializerMethodField()

    class Meta:
        model = Album
        lookup_field = 'directory'
        fields = (
            'id',
            'title',
            'date',
            'description',
            'parent_albums',
            'public',
            'photos'
        )
        extra_kwargs = {
            'url': {'lookup_field': 'directory'}
        }

    def get_parent_albums(self, obj):
        albums = []
        current_album = obj.parent
        while current_album is not None:
            album = {
                'id': current_album.id,
                'title': current_album.title,
                'slug': current_album.directory
            }
            albums.append(album)
            current_album = current_album.parent
        albums.reverse()
        return albums
