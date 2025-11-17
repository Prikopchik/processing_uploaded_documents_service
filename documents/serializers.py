from rest_framework import serializers

from .models import Document


class DocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ["id", "user", "file", "status", "created_at", "updated_at"]
        read_only_fields = ["id", "user", "status", "created_at", "updated_at"]


