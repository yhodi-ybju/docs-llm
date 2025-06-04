from django.db import models

class Document(models.Model):
    filename = models.CharField(max_length=255)
    filepath = models.CharField(max_length=1024)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.filename

class Chunk(models.Model):
    document = models.ForeignKey(
        Document,
        related_name='chunks',
        on_delete=models.CASCADE
    )
    content = models.TextField()

    def __str__(self):
        return f"Chunk {self.id} of {self.document.filename}"

class QueryRecord(models.Model):
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Q: {self.question[:1000]}"