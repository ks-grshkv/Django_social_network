import shutil
import tempfile
from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from posts.forms import PostForm, CommentForm

from ..models import Group, Post, User, Comment

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        PostCreateFormTests.guest_client = Client()
        PostCreateFormTests.authorized_client = Client()
        PostCreateFormTests.authorized_client.force_login(
            self.user
        )

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Тестов текст 123',
            'group': PostCreateFormTests.group.pk,
            'image': uploaded,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': PostCreateFormTests.user.username}
        )
        )
        test_post = Post.objects.get(
            text=form_data['text'],
            group=form_data['group'],
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                image=test_post.image
            ).exists()
        )


class CommentFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user1')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Text 123'
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='LOL'
        )
        cls.form = CommentForm()

    def setUp(self):
        CommentFormTests.authorized_client = Client()
        CommentFormTests.authorized_client.force_login(
            self.user
        )

    def test_create_comment(self):
        """Создается запись в Comment."""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                text=form_data['text'],
            ).exists()
        )
        self.assertRedirects(
            response,
            f'/posts/{self.post.id}/'
        )
