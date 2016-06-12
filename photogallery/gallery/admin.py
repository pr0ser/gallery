from django.contrib import admin
from .models import Album, Photo
from django.utils.translation import ugettext_lazy as _


class AlbumAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'date',
        'directory',
        'description',
        'parent_album',
        'public',
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
                        'preview_img',)
             }
         ),
    )
    readonly_fields = ('file_hash',)

admin.site.register(Album, AlbumAdmin)
admin.site.register(Photo, PhotoAdmin)
