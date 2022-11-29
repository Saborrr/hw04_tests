from django.contrib.auth import get_user_model
from django.test import TestCase, Client

from posts.models import Post, Group

User = get_user_model()


class TaskURLTests(TestCase):
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
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Шаблоны по адресам
        templates_url_names = {
            'posts/index.html': '/',
            'posts/group_list.html': '/group/vvv/',
            'posts/profile.html': '/profile/auth/',
            'posts/post_detail.html': '/posts/1/',
            'posts/create_post.html': '/create/',
        }
        for template, address in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/group/vvv/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/profile/auth/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/posts/1/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('404')
        self.assertEqual(response.status_code, 404)

        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, 200)

        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, 302)

    def test_unexisting_page(self):
        """Тест несуществующей страницы"""
        response = self.authorized_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, 404)
