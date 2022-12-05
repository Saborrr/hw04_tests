from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Comment, Post, User


class CommentTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_user = User.objects.create(username='comment')
        cls.post = Post.objects.create(
            text='Редактируемый текст',
            author=cls.test_user,
        )
        cls.comment_url = reverse('posts:add_comment', args=['1'])

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.test_user)

    def test_authorized_client_comment(self):
        """Авторизированный пользователь может комментировать"""
        text_comment = 'Тестовый комментарий'
        self.authorized_client.post(CommentTests.comment_url,
                                    data={'text': text_comment}
                                    )
        comment = Comment.objects.filter(post=CommentTests.post).last()
        self.assertEqual(comment.text, text_comment)
        self.assertEqual(comment.post, CommentTests.post)
        self.assertEqual(comment.author, CommentTests.test_user)

    def test_guest_client_comment_redirect_login(self):
        """Неавторизированный пользователь не может комментаровать"""
        count_comments = Comment.objects.count()
        self.guest_client.post(CommentTests.comment_url)
        self.assertEqual(count_comments, Comment.objects.count())
