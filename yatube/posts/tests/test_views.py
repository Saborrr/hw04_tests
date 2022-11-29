from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_user'),
            text='Тестовый пост',
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)

    def index_page_contains_page_obj(self):
        """Вывод page_obj на главной странице"""
        responce = self.authorized_client.get(reverse('posts:index'))
        self.check_post_info(responce.context['page_obj'][0])
        """Вывод page_obj на странице group_list.html"""
        responce = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(responce.context['group'], self.group)
        self.check_post_info(responce.context['page_obj'][0])

    def test_profile_page_contains_auth_page_profile(self):
        """Вывод 'auth' и 'page_obj' в profile.html"""
        responce = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(responce.context['author'], self.user)
        # self.check_post_info(responce.context['page_obj'][0])

        """Вывод 'post' на post_detail.html"""
        responce = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        # self.check_post_info(responce.context['post'])


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth',)
        cls.group = Group.objects.create(
            title='Тестовое название группы',
            slug='slug',
            description='Описание группы',
        )
        cls.post = []
        for i in range(15):
            Post.objects.create(
                text=f'Пост № {i}',
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.unauthorized_client = Client()

    def test_paginator_on_pages(self):
        """Проверка пагинации на страницах"""
        posts_on_first_page = 10
        posts_on_second_page = 5
        url_pages = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reverse_ in url_pages:
            with self.subTest(reverse_=reverse_):
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_).context.get('page_obj')),
                    posts_on_first_page
                )
                self.assertEqual(len(self.unauthorized_client.get(
                    reverse_ + '?page=2').context.get('page_obj')),
                    posts_on_second_page
                )
