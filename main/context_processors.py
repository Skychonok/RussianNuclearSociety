from .models import SiteSettings, Banner, Category
from django.utils import timezone

def global_site_context(request):
    try:
        settings = SiteSettings.load()
        main_menu = Category.objects.filter(
            is_active=True,
            parent=None
        ).prefetch_related('children')

        active_banners = Banner.objects.filter(is_active=True)

    except Exception:
        settings, main_menu, active_banners = None, [], []

    return {
        'site_settings': settings,
        'main_menu': main_menu,
        'sidebar_banners': active_banners,
        'current_year': timezone.now().year,
    }