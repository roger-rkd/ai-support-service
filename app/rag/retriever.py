"""
Document Retriever using FAISS Vector Database
"""

from typing import List, Tuple
import logging
import os
from pathlib import Path
import faiss
import numpy as np
from pypdf import PdfReader
from app.rag.embedder import Embedder

logger = logging.getLogger(__name__)


class DocumentRetriever:
    """
    Handles document storage and retrieval using FAISS vector database
    """

    def __init__(
        self,
        embedder: Embedder,
        data_dir: str = "data",
        index_path: str = "data/faiss.index"
    ):
        """
        Initialize the document retriever

        Args:
            embedder: Embedder instance for creating embeddings
            data_dir: Directory containing text documents
            index_path: Path to save/load FAISS index
        """
        self.embedder = embedder
        self.data_dir = Path(data_dir)
        self.index_path = Path(index_path)
        self.documents: List[str] = []
        self.index = None
        self._initialize()

    def _initialize(self) -> None:
        """Initialize or load the FAISS index"""
        if self.index_path.exists():
            logger.info("Loading existing FAISS index")
            self._load_index()
        else:
            logger.info("Creating new FAISS index from documents")
            self._create_index()

    def _load_documents(self) -> List[str]:
        """
        Load all text and PDF documents from the data directory

        Returns:
            List of document texts
        """
        documents = []

        if not self.data_dir.exists():
            logger.warning(f"Data directory {self.data_dir} does not exist")
            return documents

        # Load all .txt and .pdf files from data directory
        txt_files = list(self.data_dir.glob("*.txt"))
        pdf_files = list(self.data_dir.glob("*.pdf"))
        all_files = txt_files + pdf_files

        if not all_files:
            logger.warning(f"No .txt or .pdf files found in {self.data_dir}")
            return documents

        logger.info(f"Found {len(txt_files)} .txt and {len(pdf_files)} .pdf files in {self.data_dir}")

        # Load .txt files
        for txt_file in txt_files:
            try:
                with open(txt_file, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                    if content:
                        documents.append(content)
                        logger.debug(f"Loaded text document: {txt_file.name}")
            except Exception as e:
                logger.error(f"Failed to load {txt_file}: {str(e)}")

        # Load .pdf files
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(str(pdf_file))
                pdf_text = ""
                for page_num, page in enumerate(reader.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pdf_text += page_text + "\n"

                content = pdf_text.strip()
                if content:
                    documents.append(content)
                    logger.debug(f"Loaded PDF document: {pdf_file.name} ({len(reader.pages)} pages)")
            except Exception as e:
                logger.error(f"Failed to load PDF {pdf_file}: {str(e)}")

        logger.info(f"Successfully loaded {len(documents)} documents")
        return documents

    def _create_index(self) -> None:
        """Create a new FAISS index from documents"""
        # Load documents
        self.documents = self._load_documents()

        if not self.documents:
            logger.warning("No documents to index. Creating empty index.")
            # Create empty index
            dimension = self.embedder.get_embedding_dimension()
            self.index = faiss.IndexFlatIP(dimension)  # Inner product for normalized vectors
            return

        # Generate embeddings
        embeddings = self.embedder.embed_documents(self.documents)

        # Create FAISS index (Inner Product for normalized embeddings = cosine similarity)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatIP(dimension)

        # Add embeddings to index
        self.index.add(embeddings.astype(np.float32))

        logger.info(f"Created FAISS index with {self.index.ntotal} vectors")

        # Save index
        self._save_index()

    def _save_index(self) -> None:
        """Save FAISS index to disk"""
        try:
            # Create directory if it doesn't exist
            self.index_path.parent.mkdir(parents=True, exist_ok=True)

            # Save index
            faiss.write_index(self.index, str(self.index_path))

            # Save documents list
            docs_path = self.index_path.with_suffix(".docs.txt")
            with open(docs_path, "w", encoding="utf-8") as f:
                for doc in self.documents:
                    # Replace newlines with special marker for multi-line docs
                    doc_escaped = doc.replace("\n", "\\n")
                    f.write(f"{doc_escaped}\n")

            logger.info(f"Saved FAISS index to {self.index_path}")
        except Exception as e:
            logger.error(f"Failed to save FAISS index: {str(e)}")
            raise

    def _load_index(self) -> None:
        """Load FAISS index from disk"""
        try:
            self.index = faiss.read_index(str(self.index_path))

            # Load documents list
            docs_path = self.index_path.with_suffix(".docs.txt")
            if docs_path.exists():
                with open(docs_path, "r", encoding="utf-8") as f:
                    self.documents = [
                        line.strip().replace("\\n", "\n")
                        for line in f.readlines()
                    ]

            logger.info(f"Loaded FAISS index with {self.index.ntotal} vectors")
        except Exception as e:
            logger.error(f"Failed to load FAISS index: {str(e)}")
            raise

    def retrieve(self, query: str, top_k: int = 3) -> List[Tuple[str, float]]:
        """
        Retrieve the most relevant documents for a query

        Args:
            query: Query text
            top_k: Number of top documents to retrieve

        Returns:
            List of (document, score) tuples
        """
        if not self.index or self.index.ntotal == 0:
            logger.warning("Index is empty, returning no results")
            return []

        try:
            # Embed query
            query_embedding = self.embedder.embed_query(query)

            if query_embedding.size == 0:
                logger.warning("Empty query embedding")
                return []

            # Search in FAISS index
            query_embedding = query_embedding.reshape(1, -1).astype(np.float32)
            top_k = min(top_k, self.index.ntotal)  # Don't request more than available

            scores, indices = self.index.search(query_embedding, top_k)

            # Prepare results
            results = []
            for score, idx in zip(scores[0], indices[0]):
                if idx < len(self.documents):
                    results.append((self.documents[idx], float(score)))

            logger.info(f"Retrieved {len(results)} documents for query")
            return results

        except Exception as e:
            logger.error(f"Failed to retrieve documents: {str(e)}")
            raise

    def rebuild_index(self) -> None:
        """Rebuild the FAISS index from scratch"""
        logger.info("Rebuilding FAISS index")
        self._create_index()
