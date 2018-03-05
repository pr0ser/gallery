import tempfile

from PIL import Image
from django.contrib.auth.models import User
from django.test import TestCase, override_settings
from django.urls import reverse

from gallery.models import Album, Photo


def get_temporary_image(temp_file, width, height):
    image = Image.new("RGB", (width, height))
    image.save(temp_file, format='JPEG')
    return temp_file


class TestLoginLogoutViews(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('user', 'user@domain.tld', 'user')

    def test_login_page_loads(self):
        response = self.client.get(reverse('gallery:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'login')
        self.assertContains(response, 'password')

    def test_login(self):
        self.client.login(username=self.user.username, password='user')
        response = self.client.get(reverse('gallery:login'))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.context['user'].is_authenticated)
        self.assertContains(response, 'sidebar')

    def test_logout(self):
        self.client.login(username=self.user.username, password='user')
        response = self.client.get(reverse('gallery:logout'), follow=True)
        self.assertFalse(response.context['user'].is_authenticated)
        self.assertRedirects(response, reverse('gallery:index'))


class TestEmptyIndexView(TestCase):
    def setUp(self):
        self.response = self.client.get(reverse('gallery:index'))

    def test_view_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'index.html')

    def test_no_sidebar(self):
        self.assertNotContains(self.response, 'sidebar')


class TestIndexView(TestCase):
    def setUp(self):
        Album.objects.create(title='Test Album')
        Album.objects.create(title='Private Album', public=False)
        self.response = self.client.get(reverse('gallery:index'))

    def test_album_visible(self):
        self.assertContains(self.response, 'Test Album')

    def test_private_album(self):
        self.assertQuerysetEqual(self.response.context['albums'], ['<Album: Test Album>'])

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'index.html')


class TestLoggedInIndexView(TestCase):
    def setUp(self):
        Album.objects.create(title='Test Album', public=False)
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(reverse('gallery:index'))

    def test_private_album(self):
        self.assertContains(self.response, 'Test Album')
        self.assertQuerysetEqual(self.response.context['albums'], ['<Album: Test Album>'])

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'index.html')


class TestEmptyAlbumView(TestCase):
    def setUp(self):
        album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        url = reverse('gallery:album', kwargs={'slug': album.directory})
        self.response = self.client.get(url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_title(self):
        self.assertContains(self.response, 'Test Album')

    def test_description(self):
        self.assertContains(self.response, 'Test description')

    def test_no_photos(self):
        self.assertQuerysetEqual(self.response.context['photos'], [])


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestAlbumView(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        self.test_image = get_temporary_image(temp_file, width=100, height=100)
        self.photo = Photo(title='Test Photo', image=self.test_image.name, album=self.album)
        self.photo.save()
        self.url = reverse('gallery:album', kwargs={'slug': self.album.directory})
        self.response = self.client.get(self.url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'album.html')

    def test_album_has_photo(self):
        self.assertQuerysetEqual(self.response.context['photos'], ['<Photo: Test Photo>'])

    def test_title(self):
        self.assertContains(self.response, 'Test Album')

    def test_description(self):
        self.assertContains(self.response, 'Test description')

    def test_page_loads_logged_in(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(self.response.context['user'].is_authenticated)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestAlbumLargeView(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        self.test_image = get_temporary_image(temp_file, width=100, height=100)
        self.photo = Photo(title='Test Photo', image=self.test_image.name, album=self.album)
        self.photo.save()
        self.url = reverse('gallery:album-large', kwargs={'slug': self.album.directory})
        self.response = self.client.get(self.url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'album-large.html')

    def test_album_has_photo(self):
        self.assertQuerysetEqual(self.response.context['photos'], ['<Photo: Test Photo>'])

    def test_title(self):
        self.assertContains(self.response, 'Test Album')

    def test_description(self):
        self.assertContains(self.response, 'Test description')

    def test_page_loads_logged_in(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(self.response.context['user'].is_authenticated)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestPhotoView(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        self.test_image = get_temporary_image(temp_file, width=100, height=100)
        self.photo = Photo(title='Test Photo', image=self.test_image.name, album=self.album)
        self.photo.save()
        self.url = reverse('gallery:photo', kwargs={'slug': self.photo.slug})
        self.response = self.client.get(self.url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'photo.html')

    def test_title(self):
        self.assertContains(self.response, 'Test Photo')

    def test_page_loads_logged_in(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(self.response.context['user'].is_authenticated)


class TestNewPhotoView(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(reverse('gallery:photo-new'))

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'photo-new.html')

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.get(reverse('gallery:photo-new'))
        self.assertRedirects(self.response, '/login/?next=/photo/new', status_code=302)


class TestNewAlbumView(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(reverse('gallery:album-new'))

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'album-new.html')

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.get(reverse('gallery:album-new'))
        self.assertRedirects(self.response, '/login/?next=/album/new', status_code=302)


class TestPhotoMassUploadView(TestCase):
    def setUp(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(reverse('gallery:photo-massupload'))

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'photo-massupload.html')

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.get(reverse('gallery:photo-massupload'))
        self.assertRedirects(self.response, '/login/?next=/upload', status_code=302)


class TestAlbumEditView(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.url = reverse('gallery:album-edit', kwargs={'slug': self.album.directory})
        self.response = self.client.get(self.url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'album-edit.html')

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, '/login/?next=/album/test-album/edit', status_code=302)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestPhotoEditView(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        self.test_image = get_temporary_image(temp_file, width=100, height=100)
        self.photo = Photo(title='Test Photo', image=self.test_image.name, album=self.album)
        self.photo.save()
        self.url = reverse('gallery:photo-edit', kwargs={'slug': self.photo.slug})
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'photo-edit.html')

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, '/login/?next=/photo/test-photo/edit', status_code=302)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestPhotoCoverView(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        self.test_image = get_temporary_image(temp_file, width=100, height=100)
        self.photo = Photo(title='Test Photo', image=self.test_image.name, album=self.album)
        self.photo.save()
        self.url = reverse('gallery:photo-setascover', kwargs={'slug': self.photo.slug})
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'photo-cover.html')

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, '/login/?next=/photo/test-photo/cover', status_code=302)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestPhotoMapView(TestCase):
    def setUp(self):
        self.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        self.test_image = get_temporary_image(temp_file, width=100, height=100)
        self.photo = Photo(title='Test Photo', image=self.test_image.name, album=self.album)
        self.photo.save()
        self.url = reverse('gallery:photo-map', kwargs={'slug': self.photo.slug})
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'photo-map.html')

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, '/login/?next=/photo/test-photo/map', status_code=302)
