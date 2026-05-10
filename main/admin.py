from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, SiteSettings, MenuItem, Category, Tag, Banner, Article, Comment, Page, Event

# Миксин для подключения TinyMCE к админке
class TinyMCEAdminMixin:
    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.8.3/tinymce.min.js',
            'js/admin_tinymce.js',
        )

@admin.register(Page)
class PageAdmin(TinyMCEAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')

@admin.register(Event)
class EventAdmin(TinyMCEAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'event_date', 'is_active')
    list_filter = ('is_active', 'event_date')

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Дополнительная информация', {'fields': ('nickname', 'avatar')}),
    )

@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)

@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'parent', 'order')
    list_editable = ('order',)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'columns_count')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'created_at', 'is_approved')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'created_at')

@admin.register(Article)
class ArticleAdmin(TinyMCEAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'category', 'is_published', 'created_at')
    list_filter = ('is_published', 'category')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')