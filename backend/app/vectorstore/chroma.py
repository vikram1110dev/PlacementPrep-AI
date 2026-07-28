from langchain_chroma import Chroma
from app.embeddings.huggingface import EmbeddingsManager
import os

VECTOR_STORE_DIR = os.path.join(os.getcwd(), "chroma_db")

class VectorStoreManager:
    _db = None
    
    @classmethod
    def get_db(cls):
        if cls._db is None:
            embeddings = EmbeddingsManager.get_embeddings()
            os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
            cls._db = Chroma(
                collection_name="placement_prep_knowledge",
                embedding_function=embeddings,
                persist_directory=VECTOR_STORE_DIR
            )
        return cls._db

    @classmethod
    def add_texts(cls, texts: list[str], metadatas: list[dict] = None):
        db = cls.get_db()
        db.add_texts(texts=texts, metadatas=metadatas)

    @classmethod
    def similarity_search(cls, query: str, k: int = 4):
        db = cls.get_db()
        return db.similarity_search(query, k=k)
