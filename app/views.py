import os
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.parsers import MultiPartParser, FormParser

from .serializers import (
    DocumentUploadSerializer,
    DocumentListSerializer,
    QuerySerializer,
    AnswerSerializer,
    QueryRecordSerializer
)
from .models import Document, QueryRecord
from .services import DocumentIndexingService
from .tasks import index_pdf

file_param = openapi.Parameter(
    name='file', in_=openapi.IN_FORM,
    description='PDF файл для загрузки',
    type=openapi.TYPE_FILE, required=True
)

class DocumentUploadView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser,
    ]
    @swagger_auto_schema(
        operation_description="Загрузить PDF и запустить фоновую индексацию",
        manual_parameters=[file_param],
        responses={
            202: openapi.Response(
                description="Accepted",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={'task_id': openapi.Schema(type=openapi.TYPE_STRING)}
                )
            ),
            400: 'Bad Request'
        },
        consumes=['multipart/form-data'],
        tags=['documents'],
    )
    def post(self, request):
        serializer = DocumentUploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        upload = serializer.validated_data['file']
        upload_dir = os.path.join(settings.MEDIA_ROOT)
        os.makedirs(upload_dir, exist_ok=True)
        file_path = os.path.join(upload_dir, upload.name)
        with open(file_path, 'wb+') as dest:
            for chunk in upload.chunks(): dest.write(chunk)
        task = index_pdf.delay(file_path)
        return Response({'task_id': task.id}, status=status.HTTP_202_ACCEPTED)

    @swagger_auto_schema(
        operation_description="Список проиндексированных документов",
        responses={
            200: openapi.Response(
                description="OK",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        ref='#/definitions/DocumentListSerializer'
                    )
                )
            )
        },
        tags=['documents'],
    )
    def get(self, request):
        docs = Document.objects.all()
        serializer = DocumentListSerializer(docs, many=True)
        return Response(serializer.data)

class QueryView(APIView):
    @swagger_auto_schema(
        operation_description="Задать вопрос и получить ответ",
        request_body=QuerySerializer,
        responses={200: openapi.Response(description='OK', schema=AnswerSerializer())},
        tags=['query'],
    )
    def post(self, request):
        serializer = QuerySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        question = serializer.validated_data['question']
        service = DocumentIndexingService()
        answer = service.answerQuery(question)
        QueryRecord.objects.create(question=question, answer=answer)
        return Response(AnswerSerializer({'answer': answer}).data)

    @swagger_auto_schema(
        operation_description="Получить историю вопросов и ответов",
        responses={
            200: openapi.Response(
                description='OK',
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        ref='#/definitions/QueryRecordSerializer'
                    )
                )
            )
        },
        tags=['query'],
    )
    def get(self, request):
        records = QueryRecord.objects.all().order_by('-created_at')
        serializer = QueryRecordSerializer(records, many=True)
        return Response(serializer.data)
