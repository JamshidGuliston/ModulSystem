from django.conf import settings
from django.core.cache import cache
from django.http import JsonResponse


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


# Token tekshiruvidan mustasno bo'lgan URL patternlar
# Login, register va admin sahifalari ochiq qoladi
PUBLIC_PATHS = [
    '/api/teachers/login/',
    '/api/students/login/',
    '/api/teachers/register/',
    '/admin/',
]


def _is_public_path(path):
    """Berilgan path ochiq (token talab qilinmaydigan) ekanligini tekshiradi."""
    for public_path in PUBLIC_PATHS:
        if path.startswith(public_path):
            return True
    return False


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
        path = request.path

        # Admin panel va statik fayllar uchun CORS tekshiruvi shart emas
        if path.startswith('/admin/') or path.startswith('/static/'):
            return self.get_response(request)

        # CORS tekshiruvi — API so'rovlari uchun
        if origin:
            if self._is_allowed(origin):
                # Preflight OPTIONS so'rovi
                if request.method == 'OPTIONS':
                    return self._preflight_response(origin)

                response = self.get_response(request)
                self._add_cors_headers(response, origin)
                return response
            else:
                # Ruxsat yo'q — CORS xatosi
                if request.method == 'OPTIONS':
                    response = JsonResponse(
                        {'detail': "Bu domendan so'rov yuborishga ruxsat yo'q."},
                        status=403
                    )
                    return response
                response = self.get_response(request)
                return response

        # Origin yo'q (brauzer emas, curl, postman va h.k.)
        # DEBUG=True bo'lganda ruxsat berish (development uchun)
        if settings.DEBUG:
            return self.get_response(request)

        # Productionda origin bo'lmasa va API so'rovi bo'lsa — rad etish
        if path.startswith('/api/') and not _is_public_path(path):
            return JsonResponse(
                {'detail': "Origin headeri talab qilinadi."},
                status=403
            )

        return self.get_response(request)

    def _is_allowed(self, origin):
        # 1. settings.py dagi statik list (development uchun)
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
