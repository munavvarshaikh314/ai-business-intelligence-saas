import faiss
import numpy as np
import os
import pickle
from typing import List, Tuple, Optional

FAISS_DIR = "app/storage/faiss_indexes"

class FAISSService:

    @staticmethod
    def _index_path(dataset_id: str) -> str:
        return os.path.join(FAISS_DIR, f"{dataset_id}.index")

    @staticmethod
    def _meta_path(dataset_id: str) -> str:
        return os.path.join(FAISS_DIR, f"{dataset_id}.meta")

    @staticmethod
    def build_index(dataset_id: str, embeddings: np.ndarray, metadata: List[dict]) -> None:
        os.makedirs(FAISS_DIR, exist_ok=True)
        dim = embeddings.shape[1]
        index = faiss.IndexFlatL2(dim)
        index.add(embeddings)
        faiss.write_index(index, FAISSService._index_path(dataset_id))
        with open(FAISSService._meta_path(dataset_id), "wb") as f:
            pickle.dump(metadata, f)

    @staticmethod
    def load_index(dataset_id: str) -> Tuple[Optional[faiss.Index], Optional[List[dict]]]:
        idx_path = FAISSService._index_path(dataset_id)
        meta_path = FAISSService._meta_path(dataset_id)
        if not os.path.exists(idx_path):
            return None, None
        index = faiss.read_index(idx_path)
        with open(meta_path, "rb") as f:
            metadata = pickle.load(f)
        return index, metadata

    @staticmethod
    def search(dataset_id: str, query_embedding: np.ndarray, top_k: int = 5) -> List[Tuple[int, float]]:
        index, metadata = FAISSService.load_index(dataset_id)
        if index is None:
            return []
        distances, indices = index.search(query_embedding, top_k)
        results = []
        for i in range(len(indices[0])):
            idx = int(indices[0][i])
            dist = float(distances[0][i])
            if idx == -1:
                continue
            similarity = float(1 / (1 + dist))
            results.append((idx, similarity))
        return results

    @staticmethod
    def delete_index(dataset_id: str) -> None:
        for path in [FAISSService._index_path(dataset_id), FAISSService._meta_path(dataset_id)]:
            if os.path.exists(path):
                os.remove(path)
