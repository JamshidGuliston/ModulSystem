from django.conf import settings
from django.core.cache import cache


CACHE_KEY = 'teacher_allowed_domains'
CACHE_TIMEOUT = 60  # 1 daqiqa


def _get_allowed_origins():
    """Bazadan teacher domenlarini oladi, 1 daqiqa cache'da saqlaydi."""
    origins = cache.get(CACHE_KEY)
    if origins is None:
        from accounts.models import Teacher
        origins = set(
            Teacher.objects.filter(domain__isnull=False, is_active=True)
            .exclude(domain='')
            .values_list('domain', flat=True)
        )
        cache.set(CACHE_KEY, origins, CACHE_TIMEOUT)
    return origins


def invalidate_domain_cache():
    """Teacher saqlanganda cache'ni tozalash uchun chaqiriladi."""
    cache.delete(CACHE_KEY)


class DynamicCORSMiddleware:
    """
    django-cors-headers o'rniga ishlatiladi.
    CORS_ALLOWED_ORIGINS (settings.py) + Teacher.domain (baza) ni tekshiradi.
    """

    CORS_HEADERS = [
        'accept',
        'accept-encoding',
        'authorization',
        'content-type',
        'dnt',
        'origin',
        'user-agent',
        'x-csrftoken',
        'x-requested-with',
    ]

    CORS_METHODS = ['DELETE', 'GET', 'OPTIONS', 'PATCH', 'POST', 'PUT']

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        origin = request.META.get('HTTP_ORIGIN', '')

        if origin and self._is_allowed(origin):
            if request.method == 'OPTIONS':
                response = self._preflight_response(origin)
                return response
            response = self.get_response(request)
            self._add_cors_headers(response, origin)
            return response

        return self.get_response(request)

    def _is_allowed(self, origin):
        # 1. settings.py dagi statik list
        static_origins = getattr(settings, 'CORS_ALLOWED_ORIGINS', [])
        if origin in static_origins:
            return True

        # 2. Bazadagi teacher domenlari
        return origin in _get_allowed_origins()

    def _preflight_response(self, origin):
        from django.http import HttpResponse
        response = HttpResponse()
        response.status_code = 200
        self._add_cors_headers(response, origin)
        response['Access-Control-Max-Age'] = '86400'
        return response

    def _add_cors_headers(self, response, origin):
        response['Access-Control-Allow-Origin'] = origin
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Methods'] = ', '.join(self.CORS_METHODS)
        response['Access-Control-Allow-Headers'] = ', '.join(self.CORS_HEADERS)
        response['Vary'] = 'Origin'
