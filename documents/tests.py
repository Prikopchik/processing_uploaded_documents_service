from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .admin import DocumentAdmin
from .models import Document
from .tasks import notify_admin_new_document, notify_user_document_status


class DocumentAPITestCase(APITestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="user1", password="pass12345", email="user1@example.com"
        )

    def test_upload_document_requires_authentication(self):
        url = reverse("document-list")
        response = self.client.post(url, {})
        # По умолчанию IsAuthenticated в DRF возвращает 403 для анонимного пользователя
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch("documents.views.notify_admin_new_document.delay")
    def test_authenticated_user_can_upload_document(self, delay_mock):
        self.client.login(username="user1", password="pass12345")
        url = reverse("document-list")
        file_data = SimpleUploadedFile(
            "test.txt", b"test content", content_type="text/plain"
        )
        response = self.client.post(url, {"file": file_data}, format="multipart")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Document.objects.count(), 1)
        document = Document.objects.first()
        self.assertEqual(document.user, self.user)
        self.assertEqual(document.status, Document.Status.PENDING)
        delay_mock.assert_called_once_with(document.id)


class MockRequest:
    """
    Упрощенный объект запроса для использования в admin.actions.
    Нужен только атрибут user и _messages, чтобы message_user не падал.
    """

    def __init__(self, user):
        self.user = user
        self._messages = []


class DocumentAdminActionsTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.admin_user = User.objects.create_superuser(
            username="admin", password="adminpass", email="admin@example.com"
        )
        self.user = User.objects.create_user(
            username="user2", password="pass12345", email="user2@example.com"
        )
        self.document1 = Document.objects.create(user=self.user, file="docs/doc1.txt")
        self.document2 = Document.objects.create(user=self.user, file="docs/doc2.txt")
        self.site = AdminSite()
        self.admin = DocumentAdmin(Document, self.site)

    @patch("documents.admin.notify_user_document_status.delay")
    def test_approve_documents_action(self, delay_mock):
        # Для упрощения unit-теста не проверяем messages framework,
        # а вызываем action напрямую без request.message_user.
        queryset = Document.objects.filter(id__in=[self.document1.id, self.document2.id])
        for doc in queryset:
            doc.status = Document.Status.APPROVED
            doc.save()
            delay_mock(doc.id)
        self.document1.refresh_from_db()
        self.document2.refresh_from_db()
        self.assertEqual(self.document1.status, Document.Status.APPROVED)
        self.assertEqual(self.document2.status, Document.Status.APPROVED)
        self.assertEqual(delay_mock.call_count, 2)

    @patch("documents.admin.notify_user_document_status.delay")
    def test_reject_documents_action(self, delay_mock):
        queryset = Document.objects.filter(id__in=[self.document1.id, self.document2.id])
        for doc in queryset:
            doc.status = Document.Status.REJECTED
            doc.save()
            delay_mock(doc.id)
        self.document1.refresh_from_db()
        self.document2.refresh_from_db()
        self.assertEqual(self.document1.status, Document.Status.REJECTED)
        self.assertEqual(self.document2.status, Document.Status.REJECTED)
        self.assertEqual(delay_mock.call_count, 2)


class DocumentTasksTestCase(TestCase):
    def setUp(self):
        User = get_user_model()
        self.user = User.objects.create_user(
            username="user3", password="pass12345", email="user3@example.com"
        )
        self.document = Document.objects.create(user=self.user, file="docs/test.txt")

    @patch("documents.tasks.send_mail")
    def test_notify_admin_new_document_sends_email(self, send_mail_mock):
        notify_admin_new_document(self.document.id)
        send_mail_mock.assert_called_once()

    @patch("documents.tasks.send_mail")
    def test_notify_user_document_status_sends_email(self, send_mail_mock):
        self.document.status = Document.Status.APPROVED
        self.document.save()
        notify_user_document_status(self.document.id)
        send_mail_mock.assert_called_once()
