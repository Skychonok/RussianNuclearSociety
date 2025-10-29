from __future__ import annotations

import uuid

from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class UUIDPrimaryKeyModel(models.Model):
    """Abstract base model that provides a UUID primary key."""
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        verbose_name=_("identifier"),
    )

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Abstract base model with creation and modification timestamps."""
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("created at"),
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("updated at"),
    )

    class Meta:
        abstract = True
        ordering = ("-created_at",)


class PublishableModel(TimeStampedModel):
    """Adds publication flags and helpers for content models."""
    is_published = models.BooleanField(
        default=False,
        verbose_name=_("is published"),
    )
    published_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("published at"),
    )

    class Meta:
        abstract = True

    def publish(self, commit: bool = True) -> None:
        self.is_published = True
        self.published_at = timezone.now()
        if commit:
            self.save(update_fields=("is_published", "published_at"))

    def unpublish(self, commit: bool = True) -> None:
        self.is_published = False
        self.published_at = None
        if commit:
            self.save(update_fields=("is_published", "published_at"))


class SoftDeletableModel(models.Model):
    """Mixin to support reversible (soft) deletion."""
    is_deleted = models.BooleanField(default=False, verbose_name=_("is deleted"))
    deleted_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("deleted at"),
    )

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False, soft: bool = True):
        if soft:
            self.is_deleted = True
            self.deleted_at = timezone.now()
            self.save(update_fields=("is_deleted", "deleted_at"))
        else:
            super().delete(using=using, keep_parents=keep_parents)

    def restore(self, commit: bool = True) -> None:
        self.is_deleted = False
        self.deleted_at = None
        if commit:
            self.save(update_fields=("is_deleted", "deleted_at"))
