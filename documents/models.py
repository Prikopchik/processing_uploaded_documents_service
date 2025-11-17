from django.conf import settings
from django.db import models


class Document(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending", "Ожидает модерации"
        APPROVED = "approved", "Подтвержден"
        REJECTED = "rejected", "Отклонен"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="documents",
    )
    file = models.FileField(upload_to="documents/")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"Document #{self.pk} by {self.user}"


# Create your models here.
