from django.contrib import admin
from django.utils.translation import ugettext_lazy as _

from .models import Album, Photo


class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'description',
        'date',
        'directory',
        'parent',
        'public',
        )
    fieldsets = (
        (_('Parent album'),
            {'fields': ('parent',)}
         ),
        (_('Album details'),
            {'fields': ('title',
                        'description',
                        'album_cover',
                        'public',
                        'sort_order',)
             }
         ),
    )


class PhotoAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'album',
        'image',
        'date',
        )
    fieldsets = (
        (_('Album'),
            {'fields': ('album',)}
         ),
        (_('Photo'),
            {'fields': ('image',)}
         ),
        (_('Photo metadata'),
            {'fields': ('title',
                        'description',
                        'file_hash',
                        'preview_img',
                        'hidpi_preview_img',
                        'thumbnail_img',
                        'hidpi_thumbnail_img',)
             }
         ),
    )
    readonly_fields = ('file_hash',)

admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
