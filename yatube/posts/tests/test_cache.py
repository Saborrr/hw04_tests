from django.core.cache import cache
from posts.models import Post, User
from django.urls import reverse
from django.test import TestCase


INDEX = reverse('posts:index')


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='ivan')
        cls.post = Post.objects.create(
            text='Тестовое описание поста',
            author=cls.test_user,)

    def test_pages_uses_correct_template(self):
        """Кэширование на главной странице работает корректно"""
        response = self.client.get(INDEX)
        cached_content = response.content
        Post.objects.create(text='Тестовый пост', author=self.test_user)
        response = self.client.get(INDEX)
        self.assertEqual(cached_content, response.content)
        cache.clear()
        response = self.client.get(INDEX)
        self.assertNotEqual(cached_content, response.content)
