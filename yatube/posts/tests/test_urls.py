from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from posts.models import Post, Group
from http import HTTPStatus
from django.shortcuts import get_object_or_404

User = get_user_model()

COUNT = 1


class StaticURLTests(TestCase):
    def test_homepage(self):
        guest_client = Client()
        response = guest_client.get('/')
        self.assertEqual(response.status_code, 200)


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=User.objects.create_user(username='test_user')
        )
        cls.group = Group.objects.create(
            title='test group',
            slug='vvv',
            description='test description',
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_post_detail_url_exists_at_desired_location(self):
        """Проверка доступности страниц любому пользователю"""
        url_names = [
            '/',
            '/group/vvv/',
            '/profile/auth/',
            f'/posts/{COUNT}/',
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_post_detail_url_exists_at_desired_location_authorized(self):
        """Проверка доступности страниц авторизованному пользователю"""
        url_names = [
            '/',
            '/group/vvv/',
            f'/posts/{COUNT}/',
            '/profile/auth/',
            '/create/',
        ]
        for url in url_names:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_home_url_exists_for_author(self):
        """Проверка доступности страниц только автору"""
        url_names = [
            f'/posts/{COUNT}/edit',
        ]
        for url in url_names:
            with self.subTest(url=url):
                post_user = get_object_or_404(User, username='auth')
                if post_user == self.authorized_client:
                    response = self.authorized_client.get(url)
                    self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/vvv/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': f'/posts/{COUNT}/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
