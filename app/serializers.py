from rest_framework import serializers
from .models import Document, QueryRecord

class DocumentUploadSerializer(serializers.Serializer):
    file = serializers.FileField()

class DocumentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Document
        fields = ['id', 'filename', 'uploaded_at']

class QuerySerializer(serializers.Serializer):
    question = serializers.CharField()

class AnswerSerializer(serializers.Serializer):
    answer = serializers.CharField()

class QueryRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = QueryRecord
        fields = ['id', 'question', 'answer', 'created_at']
