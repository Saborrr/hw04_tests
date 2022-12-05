from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()

SMALL_GIF = (b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B')


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создание пользователей
        cls.user = User.objects.create_user(username='auth')
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        # Создание группы в БД
        cls.group = Group.objects.create(
            title='Заголовок для тестовой группы',
            slug='slug',
            description='Тестовое описание'
        )
        # Создание поста в БД
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def test_guest_new_post(self):
        # Неавторизованный пользователь не может создавать посты
        form_data = {
            'text': 'Пост от неавторизованного пользователя',
            'group': self.group.id
        }
        self.guest_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertFalse(Post.objects.filter(
            text='Пост от неавторизованного пользователя').exists())

    def test_create_post(self):
        """Если форма валидна, создаем запись в БД"""
        posts_count = Post.objects.count()
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            'text': 'Тестовое описание',
            'group': self.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={
                    'username': PostCreateFormTests.post.author}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count + self.post.pk)
        post = Post.objects.latest('id')
        self.assertEqual(post.text, 'Тестовое описание')
        self.assertEqual(post.author.username, 'auth')
        self.assertEqual(post.group.title, 'Заголовок для тестовой группы')

    def test_edit_post(self):
        """Авторизованный пользователь может редактировать пост"""
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=SMALL_GIF,
            content_type='image/gif')
        form_data = {
            'text': 'Новое описание',
            'group': self.group.pk,
            'image': uploaded,
        }
        url = reverse('posts:post_edit', kwargs={'post_id': self.post.pk})
        response = self.authorized_client.post(
            url, data=form_data, follow=True
        )
        posts_count = Post.objects.count()
        self.post.refresh_from_db()
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertRedirects(
            response, reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group'],
            id=self.post.pk,
            author=self.post.author,
        ).exists())
