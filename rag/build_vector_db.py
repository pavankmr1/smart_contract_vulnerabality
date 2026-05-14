from pathlib import Path

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

RAG_DIR = Path(__file__).resolve().parent

embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

with open(RAG_DIR / "knowledge_base.txt", encoding="utf-8") as f:
    docs = f.read().split("\n\n")

db = FAISS.from_texts(docs, embeddings)
db.save_local(str(RAG_DIR / "vector_db"))

print("✅ Vector DB Built")
