import logging
import numpy as np
from typing import List, Dict, Optional
import re
import nltk
from collections import defaultdict
from sentence_transformers import SentenceTransformer # pyright: ignore[reportMissingImports]

nltk.download('punkt')
from nltk.tokenize import sent_tokenize

logger = logging.getLogger(__name__)
model = SentenceTransformer('all-MiniLM-L6-v2')

class VectorStore:
    """Semantic vector store with clean chunking and metadata"""

    def __init__(self):
        self.documents = {}  # doc_id -> chunk info
        self.vectors = {}    # doc_id -> embedding
        self.next_id = 1

    def add_document(self, filename: str, content: str, language: str = 'en', metadata: Optional[Dict] = None) -> List[int]:
        """Chunk and add document with metadata"""
        try:
            doc_ids = []
            chunks = self._chunk_by_sentences(content)

            for chunk in chunks:
                doc_id = self.next_id
                self.next_id += 1

                self.documents[doc_id] = {
                    'id': doc_id,
                    'filename': filename,
                    'content': chunk,
                    'language': language,
                    'metadata': metadata or {},
                    'word_count': len(chunk.split())
                }

                vector = self._create_vector(chunk)
                self.vectors[doc_id] = vector
                doc_ids.append(doc_id)

            logger.info(f"Added {len(doc_ids)} chunks from {filename}")
            return doc_ids

        except Exception as e:
            logger.error(f"Error adding document: {str(e)}")
            return []

    def search(self, query: str, limit: int = 5) -> List[Dict]:
        """Semantic search across chunks"""
        try:
            if not self.documents:
                return []

            query_vector = self._create_vector(query)
            similarities = []

            for doc_id, doc_vector in self.vectors.items():
                similarity = self._cosine_similarity(query_vector, doc_vector)
                if similarity > 0.3:
                    similarities.append((doc_id, similarity))

            similarities.sort(key=lambda x: x[1], reverse=True)

            results = []
            for doc_id, similarity in similarities[:limit]:
                doc = self.documents[doc_id]
                results.append({
                    'id': doc_id,
                    'filename': doc['filename'],
                    'content': doc['content'],
                    'language': doc['language'],
                    'metadata': doc['metadata'],
                    'similarity': similarity
                })

            return results

        except Exception as e:
            logger.error(f"Error searching documents: {str(e)}")
            return []

    def list_documents(self) -> List[Dict]:
        """List all chunks with metadata"""
        return [
            {
                'id': doc['id'],
                'filename': doc['filename'],
                'language': doc['language'],
                'word_count': doc['word_count'],
                'metadata': doc['metadata']
            }
            for doc in self.documents.values()
        ]

    def delete_document(self, doc_id: int) -> bool:
        """Delete a chunk"""
        if doc_id in self.documents:
            del self.documents[doc_id]
            del self.vectors[doc_id]
            logger.info(f"Deleted document {doc_id}")
            return True
        return False

    def _create_vector(self, text: str) -> np.ndarray:
        """Generate semantic embedding"""
        return model.encode(text, normalize_embeddings=True)

    def _chunk_by_sentences(self, text: str, max_words: int = 100) -> List[str]:
        """Chunk text into complete sentence blocks"""
        sentences = sent_tokenize(text)
        chunks = []
        current_chunk = []

        for sentence in sentences:
            current_chunk.append(sentence)
            if sum(len(s.split()) for s in current_chunk) >= max_words:
                chunks.append(" ".join(current_chunk))
                current_chunk = []

        if current_chunk:
            chunks.append(" ".join(current_chunk))

        return [chunk.strip() for chunk in chunks if len(chunk.strip()) > 30]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Cosine similarity between vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        if norm1 == 0 or norm2 == 0:
            return 0.0
        return dot_product / (norm1 * norm2)
