from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.text import slugify
from django.utils.html import strip_tags
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
import uuid

# === Настройки сайта (Singleton) ===

class SiteSettings(models.Model):
    """Глобальные настройки сайта, управляются из админки (ТЗ 3.5)"""
    title = models.CharField(max_length=200, default="Отечественное Ядерное общество", verbose_name="Заголовок сайта")
    maintenance_mode = models.BooleanField(default=False, verbose_name="Режим обслуживания")
    maintenance_message = models.TextField(blank=True, default="Сайт находится на техническом обслуживании.", verbose_name="Сообщение при обслуживании")
    allowed_admin_ips = models.TextField(blank=True, help_text="IP-адреса через запятую. Если пусто - доступ открыт всем.", verbose_name="Разрешенные IP для админки")
    footer_text = models.TextField(blank=True, default="Официальный сайт Ядерного общества", verbose_name="Текст футера")
    
    class Meta:
        verbose_name = "Настройки сайта"
        verbose_name_plural = "Настройки сайта"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj


# === Пользователи ===

class User(AbstractUser):
    """Кастомная модель пользователя с расширенными полями (ТЗ 3.3)"""
    nickname = models.CharField(max_length=50, blank=True, verbose_name="Никнейм")
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True, verbose_name="Аватар")
    newsletter_subscribed = models.BooleanField(default=True, verbose_name="Подписка на рассылку")

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"


# === Навигация и Контент ===

class MenuItem(models.Model):
    """Элемент главного динамического меню (ТЗ 3.6)"""
    title = models.CharField(max_length=100, verbose_name="Заголовок")
    url = models.CharField(max_length=200, blank=True, help_text="URL или slug", verbose_name="Ссылка")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='children', on_delete=models.CASCADE, verbose_name="Родительский пункт")
    order = models.PositiveIntegerField(default=0, verbose_name="Порядок сортировки")
    
    class Meta:
        ordering = ['order']
        verbose_name = "Пункт меню"
        verbose_name_plural = "Пункты меню"

    def __str__(self):
        return self.title


class Category(models.Model):
    """Разделы сайта с поддержкой иерархии (ТЗ 3.7, 3.8)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, unique=True, verbose_name="Название")
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, verbose_name="Описание")
    parent = models.ForeignKey('self', null=True, blank=True, related_name='subcategories', on_delete=models.CASCADE, verbose_name="Родительский раздел")
    color = models.CharField(max_length=7, default="#6c98c3", verbose_name="Цвет (HEX)")
    columns_count = models.IntegerField(default=2, choices=[(1, '1 колонка'), (2, '2 колонки'), (3, '3 колонки')], verbose_name="Отображение в колонок")
    show_preview = models.BooleanField(default=True, verbose_name="Показывать превью-картинки")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Создано")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Обновлено")
    
    class Meta:
        verbose_name = "Раздел"
        verbose_name_plural = "Разделы"
        ordering = ("name",)

    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse("main:category_detail", kwargs={"slug": self.slug})


class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ("name",)

    def __str__(self): 
        return self.name
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Banner(models.Model):
    """Управление баннерами (ТЗ 3.9)"""
    title = models.CharField(max_length=100, verbose_name="Название (для админки)")
    image = models.ImageField(upload_to="banners/", null=True, blank=True, verbose_name="Изображение баннера")
    html_content = models.TextField(blank=True, verbose_name="HTML/Текст (если нет картинки)")
    url = models.URLField(blank=True, verbose_name="Ссылка при клике")
    is_active = models.BooleanField(default=True, verbose_name="Активен")
    order = models.IntegerField(default=0, verbose_name="Порядок")

    class Meta:
        ordering = ['order']
        verbose_name = "Баннер"
        verbose_name_plural = "Баннеры"


class Page(models.Model):
    """Динамические страницы (О нас, Образование, Атомная отрасль и т.д.)"""
    title = models.CharField(max_length=200, verbose_name="Заголовок страницы")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL (slug)")
    content = models.TextField(verbose_name="Содержание (HTML)")
    
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Мета-описание")
    is_active = models.BooleanField(default=True, verbose_name="Опубликовано")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Страница"
        verbose_name_plural = "Страницы"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("main:page_detail", kwargs={"slug": self.slug})


class Event(models.Model):
    """Мероприятия (для страницы 'План мероприятий')"""
    title = models.CharField(max_length=200, verbose_name="Название мероприятия")
    event_date = models.DateTimeField(verbose_name="Дата и время проведения")
    description = models.TextField(verbose_name="Описание и повестка")
    
    is_active = models.BooleanField(default=True, verbose_name="Актуально")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-event_date']
        verbose_name = "Мероприятие"
        verbose_name_plural = "Мероприятия"

    def __str__(self):
        return f"{self.title} ({self.event_date.strftime('%d.%m.%Y')})"


# === Логика статей (QuerySet и Manager) ===

class ArticleQuerySet(models.QuerySet):
    def published(self):
        return self.filter(is_published=True, is_deleted=False)
    
    def drafts(self):
        return self.filter(is_published=False, is_deleted=False)

class ArticleManager(models.Manager):
    def get_queryset(self):
        return ArticleQuerySet(self.model, using=self._db)
    
    def published(self):
        return self.get_queryset().published()
    
    def drafts(self):
        return self.get_queryset().drafts()


class Article(models.Model):
    """Полная модель материала (ТЗ 3.10, 3.11) со всеми полями для форм"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=200, verbose_name="Заголовок")
    hide_title = models.BooleanField(default=False, verbose_name="Скрыть заголовок при выводе")
    slug = models.SlugField(max_length=200, unique=True)
    
    excerpt = models.TextField(max_length=500, blank=True, verbose_name="Анонс")
    content = models.TextField(verbose_name="Содержание (HTML)")
    
    # SEO
    meta_description = models.CharField(max_length=160, blank=True, verbose_name="Мета-описание")
    meta_keywords = models.CharField(max_length=255, blank=True, verbose_name="Мета-ключевые слова")
    
    # Media
    featured_image = models.ImageField(upload_to="articles/images/", blank=True, null=True, verbose_name="Превью (Картинка)")
    featured_image_alt = models.CharField(max_length=200, blank=True, verbose_name="Alt текст картинки")
    
    # Реляции
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="articles", verbose_name="Автор")
    hide_author_and_date = models.BooleanField(default=False, verbose_name="Скрыть автора и дату")
    
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="articles", verbose_name="Раздел")
    tags = models.ManyToManyField(Tag, blank=True, related_name="articles")
    
    # Публикация и сортировка
    is_featured = models.BooleanField(default=False, verbose_name="Рекомендуем")
    order = models.IntegerField(default=0, verbose_name="Порядок")
    view_count = models.PositiveIntegerField(default=0, verbose_name="Просмотры")
    
    is_published = models.BooleanField(default=False, verbose_name="Опубликовано")
    published_at = models.DateTimeField(null=True, blank=True)
    
    # Soft Delete
    is_deleted = models.BooleanField(default=False, verbose_name="Удалено")
    deleted_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ArticleManager()

    newsletter_sent = models.BooleanField(
        default=False,
        verbose_name="Рассылка отправлена"
    )

    class Meta:
        ordering = ["-order", "-created_at"]
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"

    def __str__(self):
        return self.title
        
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            
        if not self.excerpt and self.content:
            # ИСПРАВЛЕНИЕ: Безопасное удаление тегов с помощью встроенного парсера Django
            clean_content = strip_tags(self.content).strip()
            self.excerpt = clean_content[:500] + "..." if len(clean_content) > 500 else clean_content
            
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]
            
        super().save(*args, **kwargs)

    def delete(self, using=None, keep_parents=False, soft=True):
        """Мягкое удаление, требуемое для ArticleDeleteView"""
        if soft:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=("is_deleted", "deleted_at"))
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def publish(self):
        self.is_published = True
        self.published_at = timezone.now()
        self.save(update_fields=("is_published", "published_at"))

    def unpublish(self):
        self.is_published = False
        self.published_at = None
        self.save(update_fields=("is_published", "published_at"))

    def get_absolute_url(self):
        return reverse("main:article_detail", kwargs={"slug": self.slug})

    def get_edit_url(self):
        return reverse("main:article_edit", kwargs={"slug": self.slug})

    def get_delete_url(self):
        return reverse("main:article_delete", kwargs={"slug": self.slug})

    def increment_view_count(self):
        Article.objects.filter(pk=self.pk).update(view_count=models.F('view_count') + 1)

    @property
    def reading_time(self):
        word_count = len(self.content.split())
        return max(1, word_count // 200)

    # Права доступа (используются в Mixins)
    def can_edit(self, user):
        if not user.is_authenticated: return False
        if self.author == user: return True
        return user.is_staff or user.is_superuser

    def can_delete(self, user):
        if not user.is_authenticated: return False
        return user.is_staff or user.is_superuser

    def can_publish(self, user):
        if not user.is_authenticated: return False
        return user.is_staff or user.is_superuser


class Comment(models.Model):
    """Комментарии пользователей с премодерацией (ТЗ 3.14)"""
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Автор")
    text = models.TextField(verbose_name="Текст комментария")
    is_approved = models.BooleanField(default=False, verbose_name="Одобрен (Премодерация)")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Комментарий"
        verbose_name_plural = "Комментарии"