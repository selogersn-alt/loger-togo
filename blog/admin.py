from django.contrib import admin
from .models import Category, Tag, Post

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'category', 'status', 'created_at', 'views_count')
    list_filter = ('status', 'category', 'is_trending', 'created_at')
    search_fields = ('title', 'content')
    prepopulated_fields = {'slug': ('title',)}
    autocomplete_fields = ('tags',)
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Contenu de l\'article', {
            'fields': ('title', 'slug', 'author', 'featured_image', 'content')
        }),
        ('Classification', {
            'fields': ('category', 'tags', 'is_trending')
        }),
        ('Statut et Visibilité', {
            'fields': ('status', 'views_count')
        }),
    )
