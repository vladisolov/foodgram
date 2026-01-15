from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.viewsets import GenericViewSet, ModelViewSet

from .models import Subscription
from .serializers import (
    AvatarSerializer, SetPasswordSerializer, SubscriptionSerializer,
    UserReadSerializer, UserWriteSerializer
)

User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ('get', 'post', 'head', 'options')
    permission_classes = (AllowAny,)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserWriteSerializer
        return UserReadSerializer

    @action(
        methods=('GET',), detail=False, url_path='me',
        permission_classes=(IsAuthenticated,)
    )
    def user_info(self, request):
        return Response(self.get_serializer(request.user).data)

    @action(
        methods=('POST',), detail=False,
        permission_classes=(IsAuthenticated,)
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        user = request.user
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['PUT', 'DELETE'])
@permission_classes((IsAuthenticated,))
def set_avatar(request):
    user = request.user

    if request.method == 'PUT':
        serializer = AvatarSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    elif request.method == 'DELETE':
        if user.avatar:
            user.avatar.delete(save=False)
        user.avatar = None
        user.save(update_fields=('avatar',))
        return Response(status=status.HTTP_204_NO_CONTENT)


class SubscriptionViewSet(GenericViewSet):
    permission_classes = (IsAuthenticated,)

    def list(self, request):
        user = request.user
        subscriptions = User.objects.filter(
            followers__user=user
        ).prefetch_related('recipes')

        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscriptionSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscriptionSerializer(
            subscriptions, many=True, context={'request': request}
        )
        return Response(serializer.data)

    def create(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if user == author:
            raise ValidationError('Нельзя подписаться на самого себя.')

        if Subscription.objects.filter(user=user, author=author).exists():
            raise ValidationError('Вы уже подписаны на этого пользователя.')

        Subscription.objects.create(user=user, author=author)
        serializer = SubscriptionSerializer(
            author, context={'request': request}
        )
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def destroy(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        subscription = Subscription.objects.filter(
            user=user, author=author
        ).first()

        if not subscription:
            raise ValidationError('Вы не подписаны на этого пользователя.')

        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
