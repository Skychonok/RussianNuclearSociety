from __future__ import annotations

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from rns.apps.core.models import (
    PublishableModel,
    SoftDeletableModel,
    TimeStampedModel,
    UUIDPrimaryKeyModel,
)


class ArticleType(UUIDPrimaryKeyModel, TimeStampedModel):
    """Classification for articles (e.g., popular science, news)."""
    name = models.CharField(max_length=150, unique=True, verbose_name=_("name"))
    slug = models.SlugField(max_length=150, unique=True, verbose_name=_("slug"))
    description = models.TextField(blank=True, verbose_name=_("description"))
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("is active"),
        help_text=_("Inactive types are hidden from article creation lists."),
    )

    class Meta:
        verbose_name = _("article type")
        verbose_name_plural = _("article types")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class MediaAsset(UUIDPrimaryKeyModel, TimeStampedModel, SoftDeletableModel):
    """Digital asset that can be attached to articles or other entities."""

    class MediaType(models.TextChoices):
        IMAGE = "image", _("Image")
        VIDEO = "video", _("Video")
        AUDIO = "audio", _("Audio")
        DOCUMENT = "document", _("Document")
        DATA = "data", _("Data")
        OTHER = "other", _("Other")

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="media_assets",
        verbose_name=_("owner"),
    )
    title = models.CharField(max_length=255, verbose_name=_("title"))
    description = models.TextField(blank=True, verbose_name=_("description"))
    media_type = models.CharField(
        max_length=32,
        choices=MediaType.choices,
        default=MediaType.IMAGE,
        verbose_name=_("media type"),
    )
    file = models.FileField(
        upload_to="media/assets/%Y/%m/",
        verbose_name=_("file"),
        validators=[
            FileExtensionValidator(
                allowed_extensions=(
                    "jpg",
                    "jpeg",
                    "png",
                    "gif",
                    "webp",
                    "svg",
                    "mp4",
                    "mov",
                    "avi",
                    "mkv",
                    "mp3",
                    "wav",
                    "ogg",
                    "pdf",
                    "doc",
                    "docx",
                    "ppt",
                    "pptx",
                    "xls",
                    "xlsx",
                    "csv",
                )
            )
        ],
    )
    thumbnail = models.ImageField(
        upload_to="media/assets/thumbnails/%Y/%m/",
        null=True,
        blank=True,
        verbose_name=_("thumbnail"),
    )
    source_url = models.URLField(blank=True, verbose_name=_("source URL"))
    attributes = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("attributes"),
        help_text=_("Arbitrary structured data (dimensions, duration, metadata, etc.)."),
    )
    is_public = models.BooleanField(
        default=True,
        verbose_name=_("is public"),
        help_text=_("Controls visibility for unauthenticated users."),
    )

    class Meta:
        verbose_name = _("media asset")
        verbose_name_plural = _("media assets")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("media_type",)),
            models.Index(fields=("is_public",)),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def filename(self) -> str:
        if not self.file:
            return ""
        return self.file.name.split("/")[-1]


class Article(UUIDPrimaryKeyModel, PublishableModel, SoftDeletableModel):
    """Main content entity authored by users."""
    class ArticleStatus(models.TextChoices):
        DRAFT = "draft", _("Draft")
        REVIEW = "review", _("In review")
        PUBLISHED = "published", _("Published")
        ARCHIVED = "archived", _("Archived")

    type = models.ForeignKey(
        ArticleType,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name=_("type"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="articles",
        verbose_name=_("author"),
    )
    co_authors = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        blank=True,
        related_name="coauthored_articles",
        verbose_name=_("co-authors"),
    )
    lead_media = models.ForeignKey(
        "MediaAsset",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="lead_for_articles",
        verbose_name=_("lead media"),
        help_text=_("Primary media asset featured with the article."),
    )
    media_assets = models.ManyToManyField(
        "MediaAsset",
        through="ArticleMedia",
        related_name="articles",
        blank=True,
        verbose_name=_("media assets"),
    )
    title = models.CharField(max_length=500, verbose_name=_("title"))
    slug = models.SlugField(max_length=500, unique=True, verbose_name=_("slug"))
    summary = models.TextField(
        blank=True,
        verbose_name=_("summary"),
        help_text=_("Short synopsis displayed in lists and previews."),
    )
    body = models.TextField(verbose_name=_("body"))
    status = models.CharField(
        max_length=32,
        choices=ArticleStatus.choices,
        default=ArticleStatus.DRAFT,
        verbose_name=_("status"),
    )
    reading_time_minutes = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("estimated reading time (minutes)"),
    )
    cover_image = models.ImageField(
        upload_to="articles/covers/",
        blank=True,
        null=True,
        verbose_name=_("cover image"),
    )
    language = models.CharField(
        max_length=16,
        default="ru",
        verbose_name=_("language"),
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("metadata"),
        help_text=_("Arbitrary structured data (SEO keywords, sources, etc.)."),
    )

    class Meta:
        verbose_name = _("article")
        verbose_name_plural = _("articles")
        ordering = ("-created_at",)
        indexes = [
            models.Index(fields=("status", "is_published")),
            models.Index(fields=("type", "status")),
            models.Index(fields=("author", "status")),
        ]

    def __str__(self) -> str:
        return self.title

    @property
    def is_ready_for_publication(self) -> bool:
        return self.status in {self.ArticleStatus.REVIEW, self.ArticleStatus.PUBLISHED}

    @property
    def primary_media(self) -> "MediaAsset | None":
        if self.lead_media_id:
            return self.lead_media
        primary_link = (
            self.article_media.filter(is_primary=True)
            .select_related("media")
            .order_by("order", "created_at")
            .first()
        )
        if primary_link:
            return primary_link.media
        fallback_link = (
            self.article_media.select_related("media")
            .order_by("order", "created_at")
            .first()
        )
        return fallback_link.media if fallback_link else None


class ArticleMedia(UUIDPrimaryKeyModel, TimeStampedModel):
    """Through model representing ordered media attachments for an article."""
    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="article_media",
        verbose_name=_("article"),
    )
    media = models.ForeignKey(
        MediaAsset,
        on_delete=models.CASCADE,
        related_name="article_media",
        verbose_name=_("media"),
    )
    caption = models.CharField(
        max_length=500,
        blank=True,
        verbose_name=_("caption"),
        help_text=_("Optional caption shown with the media asset."),
    )
    credit = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("credit"),
        help_text=_("Source or authorship information."),
    )
    order = models.PositiveSmallIntegerField(
        default=0,
        verbose_name=_("display order"),
    )
    is_primary = models.BooleanField(
        default=False,
        verbose_name=_("is primary"),
        help_text=_("Use this media asset as the primary display for the article."),
    )

    class Meta:
        verbose_name = _("article media")
        verbose_name_plural = _("article media")
        ordering = ("order", "created_at")
        unique_together = ("article", "media")
        indexes = [
            models.Index(fields=("article", "order")),
            models.Index(fields=("media",)),
            models.Index(fields=("article", "is_primary")),
        ]

    def __str__(self) -> str:
        return f"{self.article} ↔ {self.media}"


class ArticleTag(UUIDPrimaryKeyModel, TimeStampedModel):
    """Keyword tags assigned to articles for navigation and search."""
    name = models.CharField(max_length=64, unique=True, verbose_name=_("name"))
    slug = models.SlugField(max_length=64, unique=True, verbose_name=_("slug"))
    description = models.TextField(blank=True, verbose_name=_("description"))
    articles = models.ManyToManyField(
        Article,
        related_name="tags",
        blank=True,
        verbose_name=_("articles"),
    )

    class Meta:
        verbose_name = _("tag")
        verbose_name_plural = _("tags")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class ArticleReaction(UUIDPrimaryKeyModel, TimeStampedModel):
    """User reactions to articles."""
    class ReactionType(models.TextChoices):
        LIKE = "like", _("Like")
        DISLIKE = "dislike", _("Dislike")
        CLAP = "clap", _("Clap")
        INSIGHTFUL = "insightful", _("Insightful")
        SUPPORT = "support", _("Support")

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="reactions",
        verbose_name=_("article"),
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="article_reactions",
        verbose_name=_("user"),
    )
    reaction = models.CharField(
        max_length=32,
        choices=ReactionType.choices,
        verbose_name=_("reaction"),
    )

    class Meta:
        verbose_name = _("article reaction")
        verbose_name_plural = _("article reactions")
        constraints = [
            models.UniqueConstraint(
                fields=("article", "user", "reaction"),
                name="unique_article_user_reaction",
            ),
        ]
        indexes = [
            models.Index(fields=("article", "reaction")),
            models.Index(fields=("user",)),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.get_reaction_display()} ({self.article})"


class ArticleComment(UUIDPrimaryKeyModel, TimeStampedModel, SoftDeletableModel):
    """Threaded discussion under an article."""
    class CommentStatus(models.TextChoices):
        PUBLISHED = "published", _("Published")
        PENDING = "pending", _("Pending moderation")
        HIDDEN = "hidden", _("Hidden")
        DELETED = "deleted", _("Deleted")

    article = models.ForeignKey(
        Article,
        on_delete=models.CASCADE,
        related_name="comments",
        verbose_name=_("article"),
    )
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="article_comments",
        verbose_name=_("author"),
    )
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="replies",
        verbose_name=_("parent comment"),
    )
    body = models.TextField(verbose_name=_("body"))
    status = models.CharField(
        max_length=32,
        choices=CommentStatus.choices,
        default=CommentStatus.PUBLISHED,
        verbose_name=_("status"),
    )
    is_edited = models.BooleanField(default=False, verbose_name=_("is edited"))
    edited_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("edited at"),
    )
    pinned = models.BooleanField(
        default=False,
        verbose_name=_("pinned"),
        help_text=_("Pinned comments are shown at the top of the thread."),
    )

    class Meta:
        verbose_name = _("article comment")
        verbose_name_plural = _("article comments")
        ordering = ("created_at",)
        indexes = [
            models.Index(fields=("article", "status")),
            models.Index(fields=("parent",)),
        ]

    def __str__(self) -> str:
        return f"{self.author or _('Deleted user')} on {self.article}"

    def mark_edited(self, commit: bool = True) -> None:
        self.is_edited = True
        self.edited_at = self.updated_at
        if commit:
