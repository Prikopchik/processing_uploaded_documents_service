from django.contrib import admin

from .models import Document
from .tasks import notify_user_document_status


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("user__username", "user__email")
    actions = ("approve_documents", "reject_documents")

    @admin.action(description="Подтвердить выбранные документы")
    def approve_documents(self, request, queryset):
        updated = queryset.update(status=Document.Status.APPROVED)
        for document in queryset:
            notify_user_document_status.delay(document.id)
        self.message_user(request, f"Подтверждено документов: {updated}")

    @admin.action(description="Отклонить выбранные документы")
    def reject_documents(self, request, queryset):
        updated = queryset.update(status=Document.Status.REJECTED)
        for document in queryset:
            notify_user_document_status.delay(document.id)
        self.message_user(request, f"Отклонено документов: {updated}")


# Register your models here.
