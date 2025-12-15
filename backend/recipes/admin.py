from django.contrib import admin
from backend.users.models import Favorite, ShoppingCart
from .models import (Ingredient, Recipe, RecipeIngredient)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_favorites_count', 'cooking_time')
    search_fields = ('name', 'author__username')
    list_filter = ('author',)
    inlines = (RecipeIngredientInline,)

    def get_favorites_count(self, obj):
        return obj.in_favorites.count()

    get_favorites_count.short_description = 'Число добавлений в избранное'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
