from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Test_group',
            slug='Test_slug',
            description='Test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Test_post',
        )

    def test_models_have_correct_names_group(self):
        """Проверяем, что у моделей корректно работает title"""
        check = PostModelTest.group
        expected_value = check.title
        self.assertEqual(expected_value, str(check))

    def test_models_have_correct_names_post(self):
        """Проверяем, что у поста 15 символов"""
        check = PostModelTest.post
        expected_value = check.text[:15]
        self.assertEqual(expected_value, str(check))
