"""
Document Embedder using Sentence Transformers
"""

from typing import List
import logging
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


class Embedder:
    """
    Handles document and query embedding using sentence-transformers
    """

    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        """
        Initialize the embedder with a specific model

        Args:
            model_name: Name of the sentence-transformers model to use
        """
        self.model_name = model_name
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the sentence transformer model"""
        try:
            logger.info(f"Loading embedding model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Embedding model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load embedding model: {str(e)}")
            raise

    def embed_documents(self, documents: List[str]) -> np.ndarray:
        """
        Embed a list of documents

        Args:
            documents: List of document texts to embed

        Returns:
            numpy array of embeddings with shape (n_documents, embedding_dim)
        """
        if not documents:
            logger.warning("No documents provided for embedding")
            return np.array([])

        try:
            logger.info(f"Embedding {len(documents)} documents")
            embeddings = self.model.encode(
                documents,
                convert_to_numpy=True,
                show_progress_bar=False,
                normalize_embeddings=True  # L2 normalization for better similarity
            )
            logger.info(f"Generated embeddings with shape: {embeddings.shape}")
            return embeddings
        except Exception as e:
            logger.error(f"Failed to embed documents: {str(e)}")
            raise

    def embed_query(self, query: str) -> np.ndarray:
        """
        Embed a single query

        Args:
            query: Query text to embed

        Returns:
            numpy array of query embedding with shape (embedding_dim,)
        """
        if not query or not query.strip():
            logger.warning("Empty query provided for embedding")
            return np.array([])

        try:
            logger.debug(f"Embedding query: {query[:50]}...")
            embedding = self.model.encode(
                query,
                convert_to_numpy=True,
                normalize_embeddings=True
            )
            return embedding
        except Exception as e:
            logger.error(f"Failed to embed query: {str(e)}")
            raise

    def get_embedding_dimension(self) -> int:
        """
        Get the embedding dimension of the model

        Returns:
            Embedding dimension size
        """
        return self.model.get_sentence_embedding_dimension()
