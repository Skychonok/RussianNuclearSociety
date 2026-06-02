from .models import SiteSettings, MenuItem, Banner
from django.utils import timezone

def global_site_context(request):
    """Глобальный контекст для динамического меню, настроек и футера"""
    try:
        settings = SiteSettings.load()
        main_menu = MenuItem.objects.filter(parent__isnull=True).prefetch_related('children')
        active_banners = Banner.objects.filter(is_active=True)
    except Exception:
        settings, main_menu, active_banners = None, [],[]

    return {
        'site_settings': settings,
        'main_menu': main_menu,
        'sidebar_banners': active_banners,
        'current_year': timezone.now().year,
    }