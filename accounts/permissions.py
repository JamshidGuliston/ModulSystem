from rest_framework.permissions import BasePermission


class IsAuthenticatedTeacher(BasePermission):
    """
    Faqat token orqali autentifikatsiya qilingan teacher ga ruxsat beradi.
    """
    message = "API ga kirish uchun to'g'ri token talab qilinadi."

    def has_permission(self, request, view):
        return hasattr(request, 'teacher') and request.teacher is not None


class IsAuthenticatedTeacherOrStudent(BasePermission):
    """
    Teacher token yoki student login orqali autentifikatsiya bo'lgan
    so'rovlarga ruxsat beradi.
    """
    message = "API ga kirish uchun autentifikatsiya talab qilinadi."

    def has_permission(self, request, view):
        # Teacher token orqali
        if hasattr(request, 'teacher') and request.teacher is not None:
            return True
        # Student sessiya orqali (agar kerak bo'lsa kelajakda)
        return False
