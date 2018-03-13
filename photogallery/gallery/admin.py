from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import ugettext_lazy as _

from gallery.models import Album, Photo, ExifData


class GalleryAdminSite(AdminSite):
    site_title = _('Gallery administration')
    site_header = _('Gallery administration')


class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'date',
        'directory',
        'parent',
        'pending_post_processing',
        'admin_thumbnail',
        'public',
    )
    fieldsets = (
        (_('Parent album'), {
            'fields': ('parent',)
        }),
        (_('Album details'), {
            'fields': (
                'title',
                'description',
                'album_cover',
                'sort_order',
                'public',
                'show_metadata',
                'show_location',
                'downloadable'
            )
        })
    )
    list_filter = (
        'public',
        'downloadable',
        'show_metadata',
        'show_location'
    )

    def get_queryset(self, request):
        return super(AlbumAdmin, self).get_queryset(request).select_related('album_cover')


class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'album',
        'image',
        'date',
        'admin_thumbnail',
        'ready',
    )
    fieldsets = (
        (_('Photo metadata'), {
            'fields': (
                'title',
                'description',
                'file_hash',
                'ready'
            )
        }),
        (_('Album'), {
            'fields': ('album',)
        }),
        (_('Photo'), {
            'fields': ('image',)
        })
    )
    readonly_fields = ('file_hash',)
    list_filter = ('album', 'ready')


class ExifAdmin(admin.ModelAdmin):
    list_display = (
        'date_taken',
        'make',
        'model',
        'iso',
        'shutter_speed',
        'aperture',
        'has_location',
        'admin_thumbnail',
    )
    fieldsets = (
        (_('Camera and photo details'), {
            'fields': (
                'date_taken',
                'make',
                'model',
                'iso',
                'shutter_speed',
                'aperture',
                'focal_length',
                'lens'
            )
        }),
        (_('Location details'), {
            'fields': (
                'has_location',
                'latitude',
                'longitude',
                'altitude',
                'locality',
                'country'
            )
        }),
    )
    list_filter = (
        'has_location',
        'make',
        'model',
        'lens',
        'locality',
        'country'
    )

    def get_queryset(self, request):
        return super(ExifAdmin, self).get_queryset(request).select_related('photo')


admin.site = GalleryAdminSite()
admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
admin.site.register(ExifData, ExifAdmin)
