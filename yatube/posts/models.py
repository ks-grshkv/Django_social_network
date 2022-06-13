from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    """
    Group model describes a category of posts
    and consists of:
    - title (name of the group),
    - description (more info about the category),
    - slug (part of the URL that is connected to a certain group),
    and a method __str__ which prints the Group title.
    """
    title = models.CharField(max_length=200)
    description = models.TextField()
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    """
    Post model describes a text post and consists of:
    - text (actual post content),
    - group (to which the post is related),
    - pub_date (date of publication, default value is the date of creation,
    of the object),
    - author (User who created the post).
    """
    text = models.TextField(
        'Текст поста',
        help_text='Введите текст поста'
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='Группа',
        help_text='Выберите группу'
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:15]


class Comment(models.Model):
    """
    Comment model describes a category of comments under a post
    and consists of:
    - comment text,
    - authour of the comment,
    - post, to which the comment is attributed.
    """
    text = models.TextField(
        'Текст комментария',
        help_text='Введите текст комментария'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name='Пост',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments',
        blank=True,
        null=True,
        verbose_name='Автор',
    )
    created = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=True
    )

    class Meta:
        ordering = ('-created',)
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return self.text[:15]


class Follow(models.Model):
    """
    Follow model describes a category of comments under a post
    and consists of:
    - comment text,
    - authour of the comment,
    - post, to which the comment is attributed.
    """
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        blank=True,
        null=True,
        verbose_name='Автор',
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        blank=True,
        null=True,
        verbose_name='Пользователь',
    )

    @classmethod
    def create(cls, user, author):
        new_follow = cls(user=user, author=author)
        return new_follow