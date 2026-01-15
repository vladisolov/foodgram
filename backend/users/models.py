from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from rest_framework.serializers import ValidationError

from .constants import (
    EMAIL_MAX_LENGTH, OBJECT_TITLE_LIMIT, USERNAME_MAX_LENGTH
)


def validate_username(username):
    """
    Функция выполняет валидацию username на соответствие формату.
    Также не допускает создание пользователя с зарезервированным username.
    """

    validator = UnicodeUsernameValidator()
    validator(username)

    if username == settings.RESERVED_USERNAME:
        raise ValidationError(
            f'Имя пользователя {username} занято.'
        )
    return username


class UserProfile(AbstractUser):
    username = models.CharField(
        max_length=USERNAME_MAX_LENGTH, unique=True,
        validators=(validate_username,)
    )
    email = models.EmailField(
        max_length=EMAIL_MAX_LENGTH, unique=True, blank=False,
        verbose_name='Адрес электронной почты'
    )
    first_name = models.CharField(
        max_length=USERNAME_MAX_LENGTH, blank=False, verbose_name='Имя'
    )
    last_name = models.CharField(
        max_length=USERNAME_MAX_LENGTH, blank=False, verbose_name='Фамилия'
    )
    avatar = models.ImageField(
        upload_to='users/',
        blank=True, null=True, verbose_name='Аватар'
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name')

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username[:OBJECT_TITLE_LIMIT]


User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Подписчик',
        related_name='subscriptions'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='Автор',
        related_name='followers'
    )

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'Подписки'
        ordering = ('user',)
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_subscription'
            ),
        )

    def clean(self):
        if self.user == self.author:
            raise ValidationError('Нельзя подписаться на самого себя.')

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'
