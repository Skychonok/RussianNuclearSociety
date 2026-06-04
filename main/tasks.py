from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings

from .models import Article, User


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_article_newsletter(self, article_id):
    try:
        article = Article.objects.get(pk=article_id)
    except Article.DoesNotExist:
        return "Article not found"

    subscribers = User.objects.filter(
        newsletter_subscribed=True
    ).exclude(email="")

    if not subscribers.exists():
        return "No subscribers"

    article_url = f"http://localhost:8000/articles/{article.slug}/"

    sent = 0
    failed = 0

    for user in subscribers.iterator():
        try:
            context = {
                "article": article,
                "article_url": article_url,
                "user": user,
            }

            subject = f"📰 {article.title}"

            html_content = render_to_string(
                "emails/article_newsletter.html",
                context
            )

            msg = EmailMultiAlternatives(
                subject=subject,
                body="Ваш почтовый клиент не поддерживает HTML-версию письма.",
                from_email=settings.EMAIL_HOST_USER,
                to=[user.email],
            )

            msg.attach_alternative(html_content, "text/html")

            msg.content_subtype = "html"

            msg.send()

            sent += 1

        except Exception:
            failed += 1
            continue

    Article.objects.filter(pk=article_id).update(
        newsletter_sent=True
    )

    return {
        "article_id": article_id,
        "sent": sent,
        "failed": failed
    }