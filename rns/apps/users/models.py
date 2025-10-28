from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from rns.apps.core.models import TimeStampedModel, UUIDPrimaryKeyModel


class Role(UUIDPrimaryKeyModel, TimeStampedModel):
    """Represents a semantic role assigned to users."""
    class RoleScope(models.TextChoices):
        GLOBAL = "global", _("Global")
        CONTENT = "content", _("Content")
        COMMUNITY = "community", _("Community")

    name = models.CharField(max_length=150, unique=True, verbose_name=_("name"))
    slug = models.SlugField(max_length=150, unique=True, verbose_name=_("slug"))
    description = models.TextField(blank=True, verbose_name=_("description"))
    scope = models.CharField(
        max_length=32,
        choices=RoleScope.choices,
        default=RoleScope.GLOBAL,
        verbose_name=_("scope"),
    )
    is_default = models.BooleanField(
        default=False,
        verbose_name=_("is default"),
        help_text=_("Automatically assign this role to newly created users."),
    )

    class Meta:
        verbose_name = _("role")
        verbose_name_plural = _("roles")
        ordering = ("name",)

    def __str__(self) -> str:
        return self.name


class User(UUIDPrimaryKeyModel, TimeStampedModel, AbstractUser):
    """Custom user model that supports role-based access."""
    email = models.EmailField(_("email address"), unique=True)
    display_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name=_("display name"),
        help_text=_("Public name displayed within the community."),
    )
    bio = models.TextField(blank=True, verbose_name=_("bio"))
    avatar = models.ImageField(
        upload_to="users/avatars/",
        blank=True,
        null=True,
        verbose_name=_("avatar"),
    )
    roles = models.ManyToManyField(
        Role,
        through="UserRole",
        related_name="users",
        blank=True,
        verbose_name=_("roles"),
    )

    REQUIRED_FIELDS = ["email"]

    class Meta(AbstractUser.Meta):
        verbose_name = _("user")
        verbose_name_plural = _("users")

    def __str__(self) -> str:
        return self.display_name or self.get_full_name() or self.username

    def assign_role(self, role: Role, *, commit: bool = True) -> "UserRole":
        user_role, _ = UserRole.objects.get_or_create(user=self, role=role)
        if commit:
            user_role.save()
        return user_role

    def remove_role(self, role: Role) -> None:
        UserRole.objects.filter(user=self, role=role).delete()

    @property
    def default_role(self) -> Role | None:
        return self.roles.filter(is_default=True).first()


class UserRole(UUIDPrimaryKeyModel, TimeStampedModel):
    """Intermediate model for user-role associations."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("user"),
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="role_memberships",
        verbose_name=_("role"),
    )
    assigned_by = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="assigned_roles",
        verbose_name=_("assigned by"),
    )

    class Meta:
        verbose_name = _("user role")
        verbose_name_plural = _("user roles")
        unique_together = ("user", "role")
        indexes = [
            models.Index(fields=("user",)),
            models.Index(fields=("role",)),
        ]

    def __str__(self) -> str:
        return f"{self.user} → {self.role}"
