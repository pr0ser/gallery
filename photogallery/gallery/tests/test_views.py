import json
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
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user('user', 'user@domain.tld', 'user')

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
    @classmethod
    def setUpTestData(cls):
        Album.objects.create(title='Test Album')
        Album.objects.create(title='Private Album', public=False)

    def setUp(self):
        self.response = self.client.get(reverse('gallery:index'))

    def test_album_visible(self):
        self.assertContains(self.response, 'Test Album')

    def test_private_album(self):
        self.assertQuerysetEqual(self.response.context['albums'], ['<Album: Test Album>'])

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'index.html')


class TestLoggedInIndexView(TestCase):
    @classmethod
    def setUpTestData(cls):
        Album.objects.create(title='Test Album', public=False)

    def setUp(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(reverse('gallery:index'))

    def test_private_album(self):
        self.assertContains(self.response, 'Test Album')
        self.assertQuerysetEqual(self.response.context['albums'], ['<Album: Test Album>'])

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'index.html')


class TestEmptyAlbumView(TestCase):
    @classmethod
    def setUpTestData(cls):
        album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        cls.url = reverse('gallery:album', kwargs={'slug': album.directory})

    def setUp(self):
        self.response = self.client.get(self.url)

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
    @classmethod
    def setUpTestData(self):
        self.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        self.test_image = get_temporary_image(temp_file, width=100, height=100)
        self.photo = Photo(title='Test Photo', image=self.test_image.name, album=self.album)
        self.photo.save()
        self.url = reverse('gallery:album', kwargs={'slug': self.album.directory})

    def setUp(self):
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
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        cls.test_image = get_temporary_image(temp_file, width=100, height=100)
        cls.photo = Photo(title='Test Photo', image=cls.test_image.name, album=cls.album)
        cls.photo.save()
        cls.url = reverse('gallery:album-large', kwargs={'slug': cls.album.directory})

    def setUp(self):
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
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        cls.test_image = get_temporary_image(temp_file, width=100, height=100)
        cls.photo = Photo(title='Test Photo', image=cls.test_image.name, album=cls.album)
        cls.photo.save()
        cls.url = reverse('gallery:photo', kwargs={'slug': cls.photo.slug})

    def setUp(self):
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
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        cls.url = reverse('gallery:album-edit', kwargs={'slug': cls.album.directory})

    def setUp(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)

    def test_page_loads(self):
        self.assertEqual(self.response.status_code, 200)

    def test_template_used(self):
        self.assertTemplateUsed(self.response, 'album-edit.html')

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.get(self.url)
        self.assertRedirects(self.response, '/login/?next=/album/test-album/edit', status_code=302)


class TestDeleteAlbumView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        cls.url = reverse('gallery:album-delete', kwargs={'slug': cls.album.directory})

    def test_delete(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.post(self.url, follow=True)
        self.assertEqual(self.response.status_code, 200)

    def test_anonymous_access(self):
        self.response = self.client.post(self.url, follow=True)
        self.assertRedirects(self.response, '/login/?next=/album/test-album/delete', status_code=302)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestPhotoEditView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        cls.test_image = get_temporary_image(temp_file, width=100, height=100)
        cls.photo = Photo(title='Test Photo', image=cls.test_image.name, album=cls.album)
        cls.photo.save()
        cls.url = reverse('gallery:photo-edit', kwargs={'slug': cls.photo.slug})

    def setUp(self):
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
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        cls.test_image = get_temporary_image(temp_file, width=100, height=100)
        cls.photo = Photo(title='Test Photo', image=cls.test_image.name, album=cls.album)
        cls.photo.save()
        cls.url = reverse('gallery:photo-setascover', kwargs={'slug': cls.photo.slug})

    def setUp(self):
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
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album',
            description='Test description'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        cls.test_image = get_temporary_image(temp_file, width=100, height=100)
        cls.photo = Photo(title='Test Photo', image=cls.test_image.name, album=cls.album)
        cls.photo.save()
        cls.url = reverse('gallery:photo-map', kwargs={'slug': cls.photo.slug})

    def setUp(self):
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


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestPhotoDeleteView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album',
            description='Test description.'
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        cls.test_image = get_temporary_image(temp_file, width=100, height=100)
        cls.photo = Photo(title='Test Photo', image=cls.test_image.name, album=cls.album)
        cls.photo.save()
        cls.url = reverse('gallery:photo-delete', kwargs={'slug': cls.photo.slug})

    def setUp(self):
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.post(self.url)

    def test_redirect(self):
        self.assertEqual(self.response.status_code, 302)

    def test_anonymous_access(self):
        self.client.logout()
        self.response = self.client.post(self.url)
        self.assertRedirects(self.response, '/login/?next=/photo/test-photo/delete', status_code=302)


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestSearchView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album ABC',
            description='Test description with special characters. Röäm.'
        )
        cls.hidden_album = Album.objects.create(
            title='Hidden Album',
            description='This is a hidden album.',
            public=False
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        cls.test_image = get_temporary_image(temp_file, width=100, height=100)
        cls.photo = Photo(
            title='Unique Photo',
            description='CBA',
            image=cls.test_image.name,
            album=cls.album
        )
        cls.photo.save()
        cls.photo2 = Photo(
            title='Just a nice photo',
            description='xyz',
            image=cls.test_image.name,
            album=cls.hidden_album
        )
        cls.photo2.save()

    def test_without_search_query(self):
        self.url = reverse('gallery:search')
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], [])

    def test_nonexisting_search_results(self):
        self.url = reverse('gallery:search') + '?q=This+query+will+not+return+anything'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], [])

    def test_template_used(self):
        self.url = reverse('gallery:search')
        self.response = self.client.get(self.url)
        self.assertTemplateUsed(self.response, 'search.html')

    def test_photo_title_search(self):
        self.url = reverse('gallery:search') + '?q=unique'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], ['<Photo: Unique Photo>'])

    def test_photo_description_search(self):
        self.url = reverse('gallery:search') + '?q=cba'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], ['<Photo: Unique Photo>'])

    def test_album_title_search(self):
        self.url = reverse('gallery:search') + '?q=abc'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], ['<Photo: Unique Photo>'])

    def test_album_description_search(self):
        self.url = reverse('gallery:search') + '?q=special'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], ['<Photo: Unique Photo>'])

    def test_special_character_search(self):
        self.url = reverse('gallery:search') + '?q=r%C3%B6%C3%A4m'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], ['<Photo: Unique Photo>'])

    def test_multi_word_search(self):
        self.url = reverse('gallery:search') + '?q=description+with+special'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], ['<Photo: Unique Photo>'])

    def test_multi_word_partial_search(self):
        self.url = reverse('gallery:search') + '?q=description+with+spec'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], ['<Photo: Unique Photo>'])

    def test_hidden_album_search(self):
        self.url = reverse('gallery:search') + '?q=xyz'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], [])

    def test_hidden_album_search_logged_in(self):
        self.url = reverse('gallery:search') + '?q=xyz'
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertQuerysetEqual(self.response.context['results'], ['<Photo: Just a nice photo>'])


@override_settings(MEDIA_ROOT=tempfile.gettempdir())
class TestSearchAPIView(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.album = Album.objects.create(
            title='Test Album ABC',
            description='Test description with special characters. Röäm.'
        )
        cls.hidden_album = Album.objects.create(
            title='Hidden Album',
            description='This is a hidden album.',
            public=False
        )
        temp_file = tempfile.NamedTemporaryFile(delete=True, suffix='.jpg')
        cls.test_image = get_temporary_image(temp_file, width=100, height=100)
        cls.photo = Photo(
            title='Unique Photo',
            description='CBA',
            image=cls.test_image.name,
            album=cls.album
        )
        cls.photo.save()
        cls.photo2 = Photo(
            title='Just a nice photo',
            description='xyz',
            image=cls.test_image.name,
            album=cls.hidden_album
        )
        cls.photo2.save()

    def test_without_search_query(self):
        self.url = reverse('gallery:search-api')
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)

    def test_nonexisting_search_results(self):
        self.url = reverse('gallery:search-api') + '?q=This+query+will+not+return+anything'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(json.loads(self.response.content)['results'], [])

    def test_photo_title_search(self):
        self.url = reverse('gallery:search-api') + '?q=unique'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        data = json.loads(self.response.content)

        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Unique Photo')
        self.assertEqual(data['results'][0]['description'], 'CBA')
        self.assertEqual(data['results'][0]['url'], self.photo.get_absolute_url())
        self.assertEqual(data['results'][0]['image'], self.photo.thumbnail_img.url)

    def test_action(self):
        self.url = reverse('gallery:search-api') + '?q=unique'
        self.response = self.client.get(self.url)
        self.assertEqual(self.response.status_code, 200)
        data = json.loads(self.response.content)

        self.assertTrue(data['action'])
        self.assertEqual(data['action']['url'], reverse('gallery:search') + '?q=unique')
        self.assertTrue(data['action']['text'])

    def test_photo_description_search(self):
        self.url = reverse('gallery:search-api') + '?q=cba'
        self.response = self.client.get(self.url)
        data = json.loads(self.response.content)

        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(data['results'][0])
        self.assertEqual(data['results'][0]['title'], 'Unique Photo')
        self.assertEqual(len(data['results']), 1)

    def test_album_title_search(self):
        self.url = reverse('gallery:search-api') + '?q=abc'
        self.response = self.client.get(self.url)
        data = json.loads(self.response.content)

        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(data['results'][0])
        self.assertEqual(data['results'][0]['title'], 'Unique Photo')
        self.assertEqual(len(data['results']), 1)

    def test_album_description_search(self):
        self.url = reverse('gallery:search-api') + '?q=special'
        self.response = self.client.get(self.url)
        data = json.loads(self.response.content)

        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(data['results'][0])
        self.assertEqual(data['results'][0]['title'], 'Unique Photo')
        self.assertEqual(len(data['results']), 1)

    def test_special_character_search(self):
        self.url = reverse('gallery:search-api') + '?q=r%C3%B6%C3%A4m'
        self.response = self.client.get(self.url)
        data = json.loads(self.response.content)

        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(data['results'][0])
        self.assertEqual(data['results'][0]['title'], 'Unique Photo')
        self.assertEqual(len(data['results']), 1)

    def test_multi_word_search(self):
        self.url = reverse('gallery:search-api') + '?q=description+with+special'
        self.response = self.client.get(self.url)
        data = json.loads(self.response.content)

        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(data['results'][0])
        self.assertEqual(data['results'][0]['title'], 'Unique Photo')
        self.assertEqual(len(data['results']), 1)

    def test_multi_word_partial_search(self):
        self.url = reverse('gallery:search-api') + '?q=description+with+spec'
        self.response = self.client.get(self.url)
        data = json.loads(self.response.content)

        self.assertEqual(self.response.status_code, 200)
        self.assertTrue(data['results'][0])
        self.assertEqual(data['results'][0]['title'], 'Unique Photo')
        self.assertEqual(len(data['results']), 1)

    def test_hidden_album_search(self):
        self.url = reverse('gallery:search-api') + '?q=xyz'
        self.response = self.client.get(self.url)
        data = json.loads(self.response.content)

        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(json.loads(self.response.content)['results'], [])

    def test_hidden_album_search_logged_in(self):
        self.url = reverse('gallery:search-api') + '?q=xyz'
        self.client.force_login(User.objects.get_or_create(username='user')[0])
        self.response = self.client.get(self.url)
        data = json.loads(self.response.content)

        self.assertEqual(self.response.status_code, 200)
        self.assertEqual(len(data['results']), 1)
        self.assertEqual(data['results'][0]['title'], 'Just a nice photo')
        self.assertEqual(data['results'][0]['description'], 'xyz')
        self.assertEqual(data['results'][0]['url'], self.photo2.get_absolute_url())
        self.assertEqual(data['results'][0]['image'], self.photo2.thumbnail_img.url)
