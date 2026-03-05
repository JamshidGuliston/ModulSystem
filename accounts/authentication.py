from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class TeacherTokenAuthentication(BaseAuthentication):
    """
    Custom token authentication.
    Frontend 'Authorization: Token <api_token>' headerini yuboradi.
    Token orqali teacher aniqlanadi va request.teacher ga biriktiriladi.
    """
    keyword = 'Token'

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')

        if not auth_header:
            return None

        parts = auth_header.split()

        if len(parts) != 2 or parts[0] != self.keyword:
            return None

        token = parts[1]

        from accounts.models import Teacher
        try:
            teacher = Teacher.objects.get(api_token=token, is_active=True)
        except Teacher.DoesNotExist:
            raise AuthenticationFailed("Noto'g'ri yoki muddati o'tgan token.")

        # request.teacher sifatida saqlash
        request.teacher = teacher

        # DRF (request.user, request.auth) formatida qaytarish
        # user=None chunki biz Django User ishlatmaymiz
        return (teacher, token)
