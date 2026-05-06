import os
import faiss
import pickle


FAISS_DIR = "app/storage/faiss_indexes"


def ensure_faiss_dir():
    if not os.path.exists(FAISS_DIR):
        os.makedirs(FAISS_DIR)


def get_index_path(dataset_id: str):
    ensure_faiss_dir()
    return os.path.join(FAISS_DIR, f"{dataset_id}.index")


def get_meta_path(dataset_id: str):
    ensure_faiss_dir()
    return os.path.join(FAISS_DIR, f"{dataset_id}_meta.pkl")


def save_faiss_index(dataset_id: str, index, metadata: list):
    index_path = get_index_path(dataset_id)
    meta_path = get_meta_path(dataset_id)

    faiss.write_index(index, index_path)

    with open(meta_path, "wb") as f:
        pickle.dump(metadata, f)


def load_faiss_index(dataset_id: str):
    index_path = get_index_path(dataset_id)
    meta_path = get_meta_path(dataset_id)

    if not os.path.exists(index_path) or not os.path.exists(meta_path):
        return None, None

    index = faiss.read_index(index_path)

    with open(meta_path, "rb") as f:
        metadata = pickle.load(f)

    return index, metadata