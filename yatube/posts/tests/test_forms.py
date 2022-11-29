from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создание авторизованного пользователя
        cls.user = User.objects.create_user(username='IvanIvanov')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)
        # Создание группы в БД
        cls.group = Group.objects.create(
            title=('Заголовок для тестовой группы'),
            slug='slug',
            description='Тестовое описание'
        )
        # Создание поста в БД
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def create_post(self):
        """Если форма валидна, создаем запись в БД"""
        posts_count = Post.objects.count()
        # Попробовал возможность добавить картинку
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content_type='/image/gif'
        )
        form_data = {
            'text': 'Данные из формы',
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
        self.assertEqual(Post.objects.count(), posts_count + 1)
        post = Post.objects.latest('id')
        self.assertEqual(post.image.name, 'posts/small.gif')
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=(1,)),
            data=form_data,
            follow=True,
        )
