from django.contrib.auth import get_user_model
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from ..models import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
from django.conf import settings


User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x01\x00'
            b'\x01\x00\x00\x00\x00\x21\xf9\x04'
            b'\x01\x0a\x00\x01\x00\x2c\x00\x00'
            b'\x00\x00\x01\x00\x01\x00\x00\x02'
            b'\x02\x4c\x01\x00\x3b'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.group = Group.objects.create(
            title='Группа',
            slug='slug',
            description='Описание группы',
        )
        cls.post = Post.objects.create(
            author=User.objects.create_user(username='test_user'),
            text='Тестовый пост',
            image=cls.uploaded,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def check_post_info(self, post):
        with self.subTest(post=post):
            self.assertEqual(post.text, self.post.text)
            self.assertEqual(post.author, self.post.author)
            self.assertEqual(post.group, self.post.group)
            self.assertEqual(post.image, self.post.image)

    def test_index_page_contains_page_obj(self):
        """Проверка контекста на главной странице."""
        responce = self.authorized_client.get(reverse('posts:index'))
        self.check_post_info(responce.context['page_obj'][0])

    def test_page_obj_on_group_list(self):
        """Проверка контекста на странице группы."""
        responce = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug})
        )
        self.assertEqual(responce.context['group'], self.group)

    def test_profile_page_contains_auth_page_profile(self):
        """Проверка контекста в профиле."""
        responce = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username})
        )
        self.assertEqual(responce.context['author'], self.user)

    def test_post_on_post_detail(self):
        """Проверка контекста на странице описания поста."""
        responce = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(responce.context['post'], self.post)
        self.check_post_info(responce.context['post'])

    def test_check_group_list_after_create_post(self):
        """Проверка, что пост не попал в группу, для которой не предназначен"""
        self.group = Group.objects.create(
            title='Группа 2',
            slug='slug-2',
            description='Описание второй группы',
        )
        response = self.authorized_client.get(reverse(
            'posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertNotIn(self.post, response.context['page_obj'])


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
        cls.post = Post.objects.bulk_create(Post(
            author=cls.user,
            text=f'Тестовый пост{i}',
            group=cls.group,
            id=f'{i}') for i in range(15))

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
