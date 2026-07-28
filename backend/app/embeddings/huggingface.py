from langchain_huggingface import HuggingFaceEmbeddings

class EmbeddingsManager:
    _instance = None
    
    @classmethod
    def get_embeddings(cls):
        if cls._instance is None:
            # Using a fast, lightweight model for sentence similarity
            cls._instance = HuggingFaceEmbeddings(
                model_name="all-MiniLM-L6-v2",
                model_kwargs={'device': 'cpu'},
                encode_kwargs={'normalize_embeddings': True}
            )
        return cls._instance
