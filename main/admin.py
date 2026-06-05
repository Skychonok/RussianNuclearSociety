from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .tasks import send_article_newsletter, send_email_task

from .models import (
    User,
    SiteSettings,
    MenuItem,
    Category,
    Tag,
    Banner,
    Article,
    Comment,
    Page,
    Event,
    EmailCampaign
)


# -----------------------------
# TinyMCE mixin
# -----------------------------
class TinyMCEAdminMixin:
    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/tinymce/6.8.3/tinymce.min.js',
            'js/admin_tinymce.js',
        )


# -----------------------------
# EMAIL ACTIONS
# -----------------------------
@admin.action(description="Отправить email выбранным пользователям")
def send_email_action(modeladmin, request, queryset):

    emails = list(
        queryset.exclude(email="").values_list("email", flat=True)
    )

    if not emails:
        return

    send_email_task.delay(
        subject="Сообщение от сайта",
        template_name="emails/custom.html",
        context={"text": "Привет! Это тестовое сообщение."},
        recipient_list=emails
    )

@admin.register(EmailCampaign)
class EmailCampaignAdmin(admin.ModelAdmin):

    list_display = (
        "subject",
        "recipient",
        "sent",
        "created_at",
    )

    readonly_fields = (
        "sent",
        "created_at",
    )

    def save_model(self, request, obj, form, change):

        is_new = obj.pk is None

        super().save_model(request, obj, form, change)

        if is_new and not obj.sent:

            send_email_task.delay(
                subject=obj.subject,
                template_name="emails/custom.html",
                context={
                    "text": obj.message
                },
                recipient_list=[
                    obj.recipient.email
                ]
            )

            obj.sent = True
            obj.save(update_fields=["sent"])

# -----------------------------
# USER ADMIN
# -----------------------------
@admin.register(User)
class CustomUserAdmin(DjangoUserAdmin):

    actions = [send_email_action]

    fieldsets = DjangoUserAdmin.fieldsets + (
        ('Дополнительная информация', {
            'fields': ('nickname', 'avatar', 'newsletter_subscribed')
        }),
    )

    list_display = (
        'username',
        'email',
        'nickname',
        'newsletter_subscribed',
        'is_staff',
        'is_active'
    )

    list_filter = (
        'is_staff',
        'is_active',
        'newsletter_subscribed'
    )


# -----------------------------
# PAGE ADMIN
# -----------------------------
@admin.register(Page)
class PageAdmin(TinyMCEAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active', 'updated_at')
    prepopulated_fields = {'slug': ('title',)}
    search_fields = ('title', 'content')


# -----------------------------
# EVENT ADMIN
# -----------------------------
@admin.register(Event)
class EventAdmin(TinyMCEAdminMixin, admin.ModelAdmin):
    list_display = ('title', 'event_date', 'is_active')
    list_filter = ('is_active', 'event_date')


# -----------------------------
# SITE SETTINGS
# -----------------------------
@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):

    def has_add_permission(self, request):
        return False if self.model.objects.count() > 0 else super().has_add_permission(request)


# -----------------------------
# MENU
# -----------------------------
@admin.register(MenuItem)
class MenuItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'parent', 'order')
    list_editable = ('order',)


# -----------------------------
# CATEGORY
# -----------------------------
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent', 'columns_count')
    prepopulated_fields = {'slug': ('name',)}


# -----------------------------
# BANNER
# -----------------------------
@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('title', 'is_active', 'order')
    list_editable = ('is_active', 'order')


# -----------------------------
# COMMENT
# -----------------------------
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('article', 'author', 'created_at', 'is_approved')
    list_editable = ('is_approved',)
    list_filter = ('is_approved', 'created_at')


# -----------------------------
# ARTICLE
# -----------------------------
@admin.register(Article)
class ArticleAdmin(TinyMCEAdminMixin, admin.ModelAdmin):

    list_display = (
        'title',
        'category',
        'is_published',
        'newsletter_sent',
        'created_at'
    )

    list_filter = (
        'is_published',
        'category'
    )

    prepopulated_fields = {
        'slug': ('title',)
    }

    search_fields = (
        'title',
        'content'
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)

        if obj.is_published and not obj.newsletter_sent:
            send_article_newsletter.delay(obj.pk)

            obj.newsletter_sent = True
            obj.save(update_fields=["newsletter_sent"])