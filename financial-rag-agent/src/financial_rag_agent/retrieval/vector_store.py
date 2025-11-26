"""
Vector store implementation using FAISS for semantic search.

Handles embedding creation, indexing, and similarity search over financial documents.
"""

import json
import logging
import pickle
from pathlib import Path
from typing import Any

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from financial_rag_agent.config import settings

logger = logging.getLogger(__name__)


class VectorStore:
    """FAISS-based vector store for semantic document retrieval."""

    def __init__(
        self,
        embedding_model: str | None = None,
        dimension: int | None = None,
        index_path: Path | None = None,
    ):
        """
        Initialize the vector store.

        Args:
            embedding_model: Sentence transformer model name
            dimension: Embedding dimension
            index_path: Path to save/load FAISS index
        """
        self.embedding_model_name = embedding_model or settings.embedding_model
        self.dimension = dimension or settings.embedding_dimension
        self.index_path = index_path or settings.vector_store_path

        # Initialize sentence transformer
        logger.info(f"Loading embedding model: {self.embedding_model_name}")
        self.encoder = SentenceTransformer(self.embedding_model_name)

        # Verify dimension matches model
        test_embedding = self.encoder.encode(["test"])
        actual_dim = test_embedding.shape[1]
        if actual_dim != self.dimension:
            logger.warning(
                f"Configured dimension {self.dimension} doesn't match model output {actual_dim}"
            )
            self.dimension = actual_dim

        # Initialize FAISS index (L2 distance)
        self.index = faiss.IndexFlatL2(self.dimension)

        # Store metadata for each indexed document
        self.documents: list[dict[str, Any]] = []
        self.doc_ids: list[int] = []

    def add_documents(self, documents: list[dict[str, Any]], text_key: str = "text") -> None:
        """
        Add documents to the vector store.

        Args:
            documents: List of document dictionaries
            text_key: Key in document dict containing text to embed
        """
        logger.info(f"Adding {len(documents)} documents to vector store")

        # Extract texts
        texts = [doc[text_key] for doc in documents]

        # Create embeddings
        logger.info("Creating embeddings...")
        embeddings = self.encoder.encode(
            texts, show_progress_bar=True, convert_to_numpy=True, normalize_embeddings=False
        )

        # Add to FAISS index
        self.index.add(embeddings.astype(np.float32))

        # Store documents and IDs
        start_id = len(self.documents)
        self.documents.extend(documents)
        self.doc_ids.extend(range(start_id, start_id + len(documents)))

        logger.info(f"Vector store now contains {len(self.documents)} documents")

    def search(
        self, query: str, top_k: int = 5, score_threshold: float | None = None
    ) -> list[dict[str, Any]]:
        """
        Search for similar documents.

        Args:
            query: Query text
            top_k: Number of results to return
            score_threshold: Minimum similarity score (optional)

        Returns:
            List of documents with scores
        """
        if self.index.ntotal == 0:
            logger.warning("Vector store is empty")
            return []

        # Create query embedding
        query_embedding = self.encoder.encode([query], convert_to_numpy=True)

        # Search FAISS index
        distances, indices = self.index.search(query_embedding.astype(np.float32), top_k)

        # Convert distances to similarity scores (inverse of L2 distance)
        # Using exponential decay: score = exp(-distance)
        scores = np.exp(-distances[0])

        # Build results
        results = []
        for idx, score in zip(indices[0], scores):
            if idx == -1:  # FAISS returns -1 for empty slots
                continue

            if score_threshold is not None and score < score_threshold:
                continue

            doc = self.documents[idx].copy()
            doc["score"] = float(score)
            results.append(doc)

        logger.info(f"Found {len(results)} documents for query")
        return results

    def save(self, path: Path | None = None) -> None:
        """
        Save the vector store to disk.

        Args:
            path: Directory path to save index and metadata
        """
        save_path = path or self.index_path
        save_path.mkdir(parents=True, exist_ok=True)

        # Save FAISS index
        index_file = save_path / "faiss.index"
        faiss.write_index(self.index, str(index_file))
        logger.info(f"Saved FAISS index to {index_file}")

        # Save documents and metadata
        metadata = {
            "documents": self.documents,
            "doc_ids": self.doc_ids,
            "dimension": self.dimension,
            "embedding_model": self.embedding_model_name,
        }
        metadata_file = save_path / "metadata.pkl"
        with open(metadata_file, "wb") as f:
            pickle.dump(metadata, f)
        logger.info(f"Saved metadata to {metadata_file}")

    def load(self, path: Path | None = None) -> bool:
        """
        Load the vector store from disk.

        Args:
            path: Directory path containing saved index

        Returns:
            True if loaded successfully, False otherwise
        """
        load_path = path or self.index_path

        index_file = load_path / "faiss.index"
        metadata_file = load_path / "metadata.pkl"

        if not index_file.exists() or not metadata_file.exists():
            logger.warning(f"Vector store files not found at {load_path}")
            return False

        try:
            # Load FAISS index
            self.index = faiss.read_index(str(index_file))
            logger.info(f"Loaded FAISS index from {index_file}")

            # Load metadata
            with open(metadata_file, "rb") as f:
                metadata = pickle.load(f)

            self.documents = metadata["documents"]
            self.doc_ids = metadata["doc_ids"]
            self.dimension = metadata["dimension"]

            logger.info(f"Loaded {len(self.documents)} documents from {metadata_file}")
            return True

        except Exception as e:
            logger.error(f"Error loading vector store: {e}")
            return False

    def clear(self) -> None:
        """Clear all documents from the vector store."""
        self.index = faiss.IndexFlatL2(self.dimension)
        self.documents = []
        self.doc_ids = []
        logger.info("Vector store cleared")

    @property
    def size(self) -> int:
        """Get number of documents in the store."""
        return len(self.documents)

    def get_stats(self) -> dict[str, Any]:
        """
        Get vector store statistics.

        Returns:
            Dictionary with statistics
        """
        return {
            "num_documents": self.size,
            "dimension": self.dimension,
            "embedding_model": self.embedding_model_name,
            "index_size_mb": self.index.ntotal * self.dimension * 4 / (1024 * 1024),
        }


def build_vector_store_from_news(
    news_data: list[dict[str, Any]], save: bool = True
) -> VectorStore:
    """
    Build a vector store from news data.

    Args:
        news_data: List of news items
        save: Whether to save the index to disk

    Returns:
        Initialized VectorStore
    """
    logger.info("Building vector store from news data")

    # Prepare documents for indexing
    documents = []
    for item in news_data:
        # Combine headline and summary for richer context
        text = f"{item['headline']}\n\n{item['summary']}"

        doc = {
            "text": text,
            "ticker": item["ticker"],
            "date": item["date"],
            "headline": item["headline"],
            "summary": item["summary"],
            "type": "news",
        }
        documents.append(doc)

    # Build vector store
    vector_store = VectorStore()
    vector_store.add_documents(documents, text_key="text")

    if save:
        vector_store.save()

    logger.info(f"Vector store built with {vector_store.size} documents")
    return vector_store


if __name__ == "__main__":
    # Test vector store creation
    logging.basicConfig(level=logging.INFO)

    from financial_rag_agent.ingestion.loader import DataLoader

    # Load news data
    loader = DataLoader()
    news = loader.load_news()

    # Build vector store
    vs = build_vector_store_from_news(news, save=True)

    # Test search
    query = "What are the main growth drivers for Apple?"
    results = vs.search(query, top_k=3)

    print(f"\nQuery: {query}\n")
    for i, result in enumerate(results, 1):
        print(f"{i}. {result['headline']}")
        print(f"   Ticker: {result['ticker']} | Score: {result['score']:.3f}")
        print(f"   Summary: {result['summary'][:100]}...\n")

    # Print stats
    print("Vector store stats:")
    stats = vs.get_stats()
    for key, value in stats.items():
        print(f"  {key}: {value}")
