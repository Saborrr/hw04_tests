from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, Post

User = get_user_model()


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
        form_data = {
            'text': 'Тестовое описание',
            'group': self.group.pk,
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
        form_data = {
            'text': 'Новое описание',
            'group': self.group.pk,
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
            # Проверяем 2 поля, так как выше в форме только 2 поля поста
            # Надеюсь все правильно сделал
            text=form_data['text'],
            group=form_data['group'],
            id=self.post.pk,
            author=self.post.author
        ).exists())
