from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from gallery.models import Album, Photo


class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'date',
        'directory',
        'parent',
        'pending_photos',
        'admin_thumbnail',
        'public',
    )
    fieldsets = (
        (_('Parent album'), {
            'fields': ('parent',)
        }),
        (_('Album details'), {
            'fields': ('title',
                       'description',
                       'album_cover',
                       'public',
                       'sort_order',)
        })
    )
    list_filter = ('public',)


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
            'fields': ('title',
                       'description',
                       'file_hash',
                       'ready')
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

admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
