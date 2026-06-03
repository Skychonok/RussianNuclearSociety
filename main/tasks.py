from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings

from .models import Article, User


@shared_task
def send_article_newsletter(article_id):

    article = Article.objects.get(pk=article_id)

    subscribers = User.objects.filter(
        newsletter_subscribed=True
    ).exclude(
        email=""
    )

    article_url = (
        f"https://your-domain.ru"
        f"{article.get_absolute_url()}"
    )

    for user in subscribers:
        send_mail(
            subject=f"Новая публикация: {article.title}",
            message=(
                f"{article.title}\n\n"
                f"{article.excerpt}\n\n"
                f"Читать:\n{article_url}"
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
        )