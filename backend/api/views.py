import base64

from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status, viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.permissions import SAFE_METHODS, IsAuthenticated
from rest_framework.response import Response

from recipes.models import Ingredient, Recipe, RecipeIngredient
from users.models_favorites import Favorite, ShoppingCart
from users.models import Subscription, User

from .filters import RecipeFilter
from .permissions import IsAuthorOrReadOnly
from .serializers import (AvatarSerializer, FavoriteSerializer,
                          IngredientSerializer,
                          RecipeCreateSerializer, RecipeReadSerializer,
                          ShoppingCartSerializer, SubscribeSerializer,
                          UserCreateSerializer, UserSerializer)


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer
    permission_classes = [permissions.AllowAny]


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    parser_classes = [JSONParser, MultiPartParser, FormParser]
    permission_classes = [permissions.AllowAny]

    def get_permissions(self):
        if self.action in ('me', 'avatar', 'set_password', 'set_email',
                           'set_username', 'subscribe', 'subscriptions'):
            return (IsAuthenticated(),)
        if self.action in ('list', 'retrieve', 'create'):
            return (permissions.AllowAny(),)
        return super().get_permissions()

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    @action(
        detail=False,
        methods=['put', 'delete'],
        url_path='me/avatar',
        permission_classes=(IsAuthenticated,),
    )
    def avatar(self, request):
        user = request.user
        if request.method == 'PUT':
            serializer = AvatarSerializer(
                user,
                data=request.data
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            user.refresh_from_db()
            return Response(serializer.data, status=status.HTTP_200_OK)

        if request.method == 'DELETE':
            if user.avatar:
                user.avatar.delete()
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
    )
    def me(self, request):
        serializer = UserSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsAuthenticated,),
    )
    def set_password(self, request):
        user = request.user
        serializer = UserSerializer(user, context={'request': request})
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')

        if not new_password:
            return Response(
                {'new_password': 'Это поле обязательно.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not current_password:
            return Response(
                {'current_password': 'Это поле обязательно.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        if not user.check_password(current_password):
            return Response(
                {'current_password': 'Текущий пароль неверный.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(new_password)
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=(IsAuthenticated,),
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        user = request.user

        if request.method == 'POST':
            if user.subscriber.filter(author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription = Subscription.objects.create(
                user=user, author=author)
            serializer = SubscribeSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            subscription = user.subscriber.filter(author=author)
            if not subscription.exists():
                return Response(
                    {'errors': 'Вы не подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            subscription.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=(IsAuthenticated,),
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = request.user

        subscriptions = User.objects.filter(
            subscribing__user=user
        ).distinct()

        page = self.paginate_queryset(subscriptions)
        if page is not None:
            serializer = SubscribeSerializer(
                page, many=True, context={'request': request}
            )
            return self.get_paginated_response(serializer.data)

        serializer = SubscribeSerializer(
            subscriptions, many=True, context={'request': request}
        )
        return Response(serializer.data)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        queryset = Ingredient.objects.all()
        ingredients = self.request.query_params.get('name')
        if ingredients is not None:
            queryset = queryset.filter(name__istartswith=ingredients)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method in SAFE_METHODS:
            return RecipeReadSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def perform_update(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if request.user.favorites.filter(recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite = Favorite.objects.create(
                user=request.user, recipe=recipe)
            serializer = FavoriteSerializer(
                favorite, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            favorite = request.user.favorites.filter(recipe=recipe)
            if not favorite.exists():
                return Response(
                    {'errors': 'Рецепта нет в избранном'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            favorite.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'])
    def get_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_code = base64.urlsafe_b64encode(
            str(recipe.id).encode()).decode()[:6]
        short_link = f"https://{request.get_host()}/s/{short_code}"

        return Response({'short-link': short_link})

    @action(detail=True, methods=['post', 'delete'],
            permission_classes=(IsAuthenticated,))
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, pk=pk)

        if request.method == 'POST':
            if request.user.shopping_cart.filter(recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart = ShoppingCart.objects.create(
                user=request.user, recipe=recipe)
            serializer = ShoppingCartSerializer(
                cart, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            cart = request.user.shopping_cart.filter(recipe=recipe)
            if not cart.exists():
                return Response(
                    {'errors': 'Рецепта нет в корзине'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            cart.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'],
            permission_classes=(IsAuthenticated,))
    def download_shopping_cart(self, request):
        ingredients = RecipeIngredient.objects.filter(
            recipe__in_shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount')).order_by('ingredient__name')

        content = ['Список покупок:\n']
        for ingredient in ingredients:
            content.append(
                f"{ingredient['ingredient__name']} "
                f"({ingredient['ingredient__measurement_unit']}) - "
                f"{ingredient['amount']}\n"
            )

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = (
            'attachment; filename="shopping_cart.txt"'
        )
        return response
