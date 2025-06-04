import logging
import ast
from pathlib import Path
from typing import List

import shutil
from PyPDF2 import PdfReader
from django.conf import settings
from django.db import transaction

from langchain.schema import Document as LangchainDocument
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.chains import RetrievalQA
from langchain_community.llms import LlamaCpp
from langchain.prompts import PromptTemplate

from app.database import DatabaseSessionLocal, initializeDatabase
from app.models import Document as DocumentModel, Chunk as ChunkModel, QueryRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PdfValidator:
    @staticmethod
    def validatePdf(filePath: str):
        if Path(filePath).suffix.lower() != ".pdf":
            raise ValueError("Only PDF files are supported")
        PdfReader(filePath)

class DocumentSplitter:
    def __init__(self, chunkSize: int = 400, chunkOverlap: int = 50):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunkSize,
            chunk_overlap=chunkOverlap
        )
    def splitDocuments(self, docs: List[LangchainDocument]) -> List[LangchainDocument]:
        return self.splitter.split_documents(docs)

class ChromaEmbeddingStore:
    def __init__(self):
        self.embedding = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL_NAME)
        self.persist_dir = str(settings.CHROMA_PERSIST_DIRECTORY)
        self.collection = "chunks"
    def addDocuments(self, docs: List[LangchainDocument]):
        Chroma.from_documents(
            docs,
            embedding=self.embedding,
            persist_directory=self.persist_dir,
            collection_name=self.collection
        )
    def getRetriever(self, topK: int = 5):
        client = Chroma(
            persist_directory=self.persist_dir,
            embedding_function=self.embedding,
            collection_name=self.collection
        )
        return client.as_retriever(search_type="similarity", search_kwargs={"k": topK})

class SaigaLanguageModel:
    def __init__(self):
        self.llmChain = LlamaCpp(
            model_path=settings.LLAMA_MODEL_PATH,
            temperature=0.3,
            top_p=0.9,
            repeat_penalty=1.1,
            max_tokens=2056,
            n_ctx=32768
        )

class DocumentIndexingService:
    def __init__(self):
        initializeDatabase()
        self.db = DatabaseSessionLocal()
        self.validator = PdfValidator()
        self.splitter = DocumentSplitter()
        self.storage = ChromaEmbeddingStore()
        self.llm = SaigaLanguageModel().llmChain
        self.stuffPrompt = PromptTemplate(
            input_variables=["context", "question"],
            template=(
                "У тебя есть несколько фрагментов документа:\n\n"
                "{context}\n\n"
                "На их основе ответь на вопрос:\n"
                "{question}\n\n"
                "Дай ответ по существу, без повторения вопроса."
            )
        )

    def _load_pdf_as_documents(self, filePath: str) -> List[LangchainDocument]:
        reader = PdfReader(filePath)
        docs: List[LangchainDocument] = []
        for i, page in enumerate(reader.pages):
            text = page.extract_text() or ""
            if text.strip():
                docs.append(LangchainDocument(page_content=text, metadata={"page": i+1}))
        return docs

    @transaction.atomic
    def indexFile(self, filePath: str) -> int:
        uploads_dir = Path(settings.BASE_DIR) / "uploads"
        uploads_dir.mkdir(parents=True, exist_ok=True)
        src = Path(filePath)
        dest = uploads_dir / src.name
        if src.resolve() != dest.resolve():
            shutil.copy(src, dest)
        self.validator.validatePdf(str(dest))
        doc = DocumentModel.objects.create(filename=dest.name, filepath=str(dest))
        raw_docs = self._load_pdf_as_documents(str(dest))
        chunks = self.splitter.splitDocuments(raw_docs)
        lc_docs: List[LangchainDocument] = []
        for chunk in chunks:
            record = ChunkModel.objects.create(document=doc, content=chunk.page_content)
            lc_docs.append(LangchainDocument(page_content=chunk.page_content, metadata={"chunk_id": record.id}))
        self.storage.addDocuments(lc_docs)
        return len(chunks)

    def answerQuery(self, questionText: str) -> str:
        retriever = self.storage.getRetriever(topK=5)
        qa = RetrievalQA.from_chain_type(
            llm=self.llm,
            chain_type="stuff",
            retriever=retriever,
            return_source_documents=False,
            chain_type_kwargs={"prompt": self.stuffPrompt}
        )
        raw_output = qa.run(questionText)
        cleaned = raw_output.replace("\\n", " ").strip()
        try:
            parsed = ast.literal_eval(cleaned)
            cleaned = parsed.get("result", cleaned)
        except Exception:
            pass
        QueryRecord.objects.create(question=questionText, answer=cleaned)
        return cleaned