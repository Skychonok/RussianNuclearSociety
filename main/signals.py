from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Article
from .tasks import send_article_newsletter


@receiver(post_save, sender=Article)
def article_published(sender, instance, **kwargs):

    if (
        instance.is_published
        and not instance.newsletter_sent
    ):
        send_article_newsletter.delay(
            str(instance.pk)
        )

        Article.objects.filter(
            pk=instance.pk
        ).update(
            newsletter_sent=True
        )