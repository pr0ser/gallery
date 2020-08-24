from django.contrib.auth.models import User
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
            'album_cover',
            'parent',
            'sort_order',
            'downloadable',
            'show_metadata',
            'show_location'
        )

    def get_photo_count(self, obj):
        if hasattr(obj, 'photocount'):
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
        ]


class AlbumSerializer(serializers.ModelSerializer):
    photos = PhotoSerializer(many=True, read_only=True, allow_null=True)
    parent_albums = serializers.SerializerMethodField()
    subalbums = AlbumListSerializer(many=True, read_only=True, allow_null=True)

    class Meta:
        model = Album
        fields = (
            'id',
            'title',
            'date',
            'description',
            'parent_albums',
            'public',
            'sort_order',
            'subalbums',
            'photos',
            'parent',
            'sort_order',
            'downloadable',
            'show_metadata',
            'show_location'
        )

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


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')
