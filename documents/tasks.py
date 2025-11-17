from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.contrib.auth import get_user_model

from .models import Document


@shared_task
def notify_admin_new_document(document_id: int) -> None:
    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        return

    subject = "Новый загруженный документ"
    message = (
        f"Пользователь {document.user} загрузил новый документ (ID: {document.id}).\n"
        f"Статус: {document.status}."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[settings.ADMIN_EMAIL],
        fail_silently=True,
    )


@shared_task
def notify_user_document_status(document_id: int) -> None:
    try:
        document = Document.objects.get(pk=document_id)
    except Document.DoesNotExist:
        return

    User = get_user_model()
    try:
        user = User.objects.get(pk=document.user_id)
    except User.DoesNotExist:
        return

    subject = "Статус вашего документа обновлен"
    message = (
        f"Ваш документ (ID: {document.id}) был {document.get_status_display().lower()}."
    )
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        fail_silently=True,
    )


