from django.contrib import admin
from .models import Ingredient, Recipe, RecipeIngredient
from users.models_favorites import Favorite, ShoppingCart


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1
    autocomplete_fields = ('ingredient',)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    search_fields = ('name',)
    list_per_page = 50


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'get_favorites_count', 'cooking_time', 'pub_date')
    search_fields = ('name', 'author__username', 'author__email')
    list_filter = ('pub_date', 'cooking_time')
    inlines = (RecipeIngredientInline,)
    readonly_fields = ('pub_date',)
    autocomplete_fields = ('author',)
    date_hierarchy = 'pub_date'

    def get_favorites_count(self, obj):
        return obj.in_favorites.count()

    get_favorites_count.short_description = 'В избранном'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    search_fields = ('user__username', 'user__email', 'recipe__name')
    autocomplete_fields = ('user', 'recipe')
