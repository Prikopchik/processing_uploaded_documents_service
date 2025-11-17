from rest_framework import viewsets, permissions

from .models import Document
from .serializers import DocumentSerializer
from .tasks import notify_admin_new_document


class IsOwner(permissions.BasePermission):
    """
    Разрешение: пользователь может видеть только свои документы.
    """

    def has_object_permission(self, request, view, obj) -> bool:
        return obj.user == request.user


class DocumentViewSet(viewsets.ModelViewSet):
    """
    API endpoint для загрузки и просмотра собственных документов.
    """

    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return Document.objects.filter(user=self.request.user).order_by("-created_at")

    def perform_create(self, serializer):
        document = serializer.save(user=self.request.user)
        # уведомление администратора об очередном документе
        notify_admin_new_document.delay(document.id)


# Create your views here.
