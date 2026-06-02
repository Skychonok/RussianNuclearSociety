from django.core.exceptions import PermissionDenied
from django.http import HttpResponse
from .models import SiteSettings

class SiteManagementMiddleware:
    """
    Промежуточное ПО для перехвата запросов (ТЗ 3.5).
    Обеспечивает режим тех. обслуживания и защиту админки по IP.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            settings = SiteSettings.load()
        except Exception:
            return self.get_response(request) # БД еще не мигрирована

        path = request.path_info
        
        # 1. Защита админки по IP
        if path.startswith('/admin/') and settings.allowed_admin_ips:
            client_ip = self.get_client_ip(request)
            allowed_ips =[ip.strip() for ip in settings.allowed_admin_ips.split(',') if ip.strip()]
            if allowed_ips and client_ip not in allowed_ips:
                raise PermissionDenied("Доступ в панель администратора запрещен для вашего IP.")

        # 2. Режим обслуживания
        if settings.maintenance_mode:
            # Исключения: админка и авторизованные админы
            if not path.startswith('/admin/') and not (request.user.is_authenticated and request.user.is_staff):
                return HttpResponse(
                    f"<h1>Техническое обслуживание</h1><p>{settings.maintenance_message}</p>",
                    status=503
                )

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')