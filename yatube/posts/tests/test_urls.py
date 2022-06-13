
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase


from ..models import Group, Post

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.author = User.objects.create_user(username='auth_of_post')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
        )
        cls.post_author = Post.objects.create(
            author=cls.author,
            text='Тестовый текст поста второго автора',
        )

        cls.public_urls = {
            'posts/index.html': '/',
            'posts/create_post.html': '/create/',
            'posts/group_list.html': f'/group/{cls.group.slug}/',
            'posts/post_detail.html': f'/posts/{cls.post.id}/',
            'posts/profile.html': f'/profile/{cls.post.author}/',
            'posts/follow.html': '/following/',
        }

        cls.urls_http_status_guest = {
            '/': HTTPStatus.OK,
            f'/profile/{cls.post.author}/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/edit/': HTTPStatus.FOUND,
            '/create/': HTTPStatus.FOUND,
            '/following/': HTTPStatus.FOUND,
            f'/posts/{cls.post.id}/comment/': HTTPStatus.FOUND,
            f'/profile/{cls.author}/follow/': HTTPStatus.FOUND,
            f'/profile/{cls.author}/unfollow/': HTTPStatus.FOUND,
        }

        cls.urls_http_status_auth = {
            '/': HTTPStatus.OK,
            f'/profile/{cls.post.author}/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/edit/': HTTPStatus.OK,
            '/create/': HTTPStatus.OK,
            '/following/': HTTPStatus.OK,
            f'/posts/{cls.post.id}/comment/': HTTPStatus.FOUND,
            f'/profile/{cls.author}/follow/': HTTPStatus.FOUND,
            f'/profile/{cls.author}/unfollow/': HTTPStatus.FOUND,
        }

    def setUp(self):
        StaticURLTests.guest_client = Client()
        StaticURLTests.authorized_client = Client()
        StaticURLTests.authorized_client.force_login(self.user)
    
    def test_auth_users_page(self):
        """Доступность авторизованным пользователям"""
        for address, template in self.urls_http_status_auth.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, template)

    def test_homepage(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for template, address in self.public_urls.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_guest_users_page(self):
        """Доступность страниц неавторизованным пользователям"""
        for address, template in self.urls_http_status_guest.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertEqual(response.status_code, template)

    def test_404_page(self):
        """404"""
        clients = (
            self.authorized_client,
            self.guest_client,
        )
        for client in clients:
            with self.subTest(address='/random_nonexistent_url/'):
                response = client.get(
                    '/random_nonexistent_url/',
                    follow=True
                )
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
                self.assertTemplateUsed(response, 'core/404.html')

