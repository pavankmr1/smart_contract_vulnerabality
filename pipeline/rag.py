from functools import lru_cache
from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

_RAG_DIR = Path(__file__).resolve().parent.parent / "rag"


@lru_cache(maxsize=1)
def _get_db():
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    return FAISS.load_local(
        str(_RAG_DIR / "vector_db"),
        embeddings,
        allow_dangerous_deserialization=True,
    )


def retrieve_knowledge(query: str) -> str:
    db = _get_db()
    docs = db.similarity_search(query, k=3)
    return "\n".join(d.page_content for d in docs)
