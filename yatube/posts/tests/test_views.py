import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

User = get_user_model()


class PostsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='Auth_user')
        cls.author = User.objects.create_user(username='New_post author')
        cls.author2 = User.objects.create_user(username='New_post author2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            group=cls.group,
            image=cls.uploaded
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            text='Тестовый коммент',
            post=cls.post
        )
        cls.group2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test-slug-two',
        )
        cls.paginated_pages = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': cls.user.username}
            ),
        }
        cls.unpaginated_pages = {
            'posts/create_post.html': reverse('posts:post_create'),
            'posts/post_detail.html': reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ),
        }
        cls.templates_page_names = {}
        cls.templates_page_names.update(cls.unpaginated_pages)
        cls.templates_page_names.update(cls.paginated_pages)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, reverse_name in self.templates_page_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_pages_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:index'))
        )
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            first_post.group.title,
            self.group.title
        )
        self.assertEqual(
            first_post.image,
            self.post.image
        )
        self.assertEqual(
            first_post.text,
            self.post.text
        )
        self.assertEqual(
            first_post.author.username,
            self.post.author.username
        )

    def test_create_post_page_show_correct_context(self):
        """Шаблон страницы создания поста
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_page_show_correct_context(self):
        """Шаблон страницы редактирования поста
        сформирован с правильным контекстом."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_group_list_pages_show_correct_context(self):
        """Шаблон group list сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        )
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            response.context.get('group').title,
            self.group.title
        )
        self.assertEqual(
            first_post.image,
            self.post.image
        )
        self.assertEqual(response.context.get('group').slug, 'test-slug')

    def test_profile_pages_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом."""
        response = (self.guest_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        )
        first_post = response.context['page_obj'][0]
        post_text = first_post.text
        post_author = first_post.author.username
        self.assertEqual(
            post_text,
            self.post.text
        )
        self.assertEqual(
            first_post.image,
            self.post.image
        )
        self.assertEqual(
            post_author,
            self.post.author.username
        )

    def test_post_detail_pages_show_correct_context(self):
        """Шаблон post detail сформирован с правильным контекстом."""
        response = (self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}))
        )
        self.assertEqual(
            response.context.get('post').text,
            self.post.text
        )
        self.assertEqual(
            response.context.get('post').image,
            self.post.image
        )
        self.assertEqual(
            response.context.get('post').author.username,
            self.user.username
        )

    def test_new_post_on_every_page_it_needs_to_be_on(self):
        """Новый пост появляется на group_list, index и profile"""
        for template, reverse_name in self.paginated_pages.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                first_post = response.context['page_obj'][0]
                self.assertEqual(
                    first_post.text,
                    self.post.text
                )
                self.assertEqual(
                    first_post.image,
                    self.post.image
                )
                self.assertEqual(
                    first_post.author.username,
                    self.user.username
                )

    def test_new_follow(self):
        """Авторизованный юзер может подписаться"""
        follows_count = Follow.objects.count()
        follow = Follow.objects.create(user=self.user, author=self.author)
        follow.save()
        response = self.authorized_client.get(
            reverse(
                'posts:profile_follow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follows_count + 1)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            )
        )

    def test_unfollow(self):
        """Авторизованный юзер может отдписаться"""
        follows_count = Follow.objects.count()
        follow = Follow.objects.create(user=self.user, author=self.author)
        follow.save()
        follow.delete()
        response = self.authorized_client.get(
            reverse(
                'posts:profile_unfollow',
                kwargs={'username': self.author.username}
            )
        )
        self.assertEqual(Follow.objects.count(), follows_count)
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': self.author.username}
            )
        )

    def test_new_post_on_following(self):
        """Новый пост появляется в подписках;
        в избранном не появляются посты от авторов, на которых
        мы не подписаны"""
        Post.objects.create(
            author=self.author,
            text='Тестовый текст поста',
            group=self.group,
        )
        post_2 = Post.objects.create(
            author=self.author2,
            text='Тестовый текст поста',
            group=self.group,
        )
        follow = Follow.objects.create(user=self.user, author=self.author)
        follow.save()
        response = self.authorized_client.get(reverse('posts:follow_index'))
        first_post = response.context['page_obj'][0]
        self.assertEqual(
            first_post.text,
            self.post.text
        )
        self.assertEqual(
            first_post.author.username,
            self.author.username
        )
        self.assertNotIn(post_2, response.context['page_obj'])

    def new_post_not_on_other_group_list_page(self):
        """Новый пост не появляется в неправильной группе"""
        response = self.authorized_client.get(
            reverse('post:profile', kwargs={'slug': 'test-slug-two'})
        )
        self.assertIsNone(response.context['page.obj'])

    def test_guest_cant_comment(self):
        """Неавторизованный юзер не может комментировать посты"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Тестовый коммент',
        }
        response = self.guest_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.pk}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
        self.assertRedirects(
            response,
            f'/auth/login/?next=/posts/{self.post.pk}/comment/'
        )


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='Auth_user2')
        cls.group1 = Group.objects.create(
            title='Тестовая группа 1',
            slug='test-slug1',
        )
        cls.posts_list = []
        for page_obj in range(0, 12):
            cls.posts_list.append(
                Post(
                    author=cls.user1,
                    text=f'Тестовый текст поста {page_obj}',
                    group=cls.group1
                )
            )
        Post.objects.bulk_create(cls.posts_list, batch_size=12)

        cls.paginated_pages = {
            'posts/index.html': reverse('posts:index'),
            'posts/group_list.html': reverse(
                'posts:group_list',
                kwargs={'slug': cls.group1.slug}
            ),
            'posts/profile.html': reverse(
                'posts:profile',
                kwargs={'username': cls.user1.username}
            ),
        }

    def setUp(self):
        self.guest_client = Client()

    def test_paginator_page1(self):
        """Проверяем пажинацию стр 1"""
        for template, reverse_name in self.paginated_pages.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']),
                    10
                )

    def test_paginator_page1(self):
        """Проверяем пажинацию стр 2"""
        for template, reverse_name in self.paginated_pages.items():
            with self.subTest(template=template):
                response = self.guest_client.get(reverse_name, {'page': 2})
                self.assertEqual(
                    len(response.context['page_obj']),
                    2
                )


class TestPostCache(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )

    def setUp(self):
        self.guest_client = Client()

    def test_cache_on_index(self):
        response = self.guest_client.get(
            reverse('posts:index')
        )
        response_new = self.guest_client.get(
            reverse('posts:index')
        )
        Post.objects.create(
            author=self.user,
            text='Тестовый текст поста',
        )
        self.assertEqual(
            response.content,
            response_new.content
        )
