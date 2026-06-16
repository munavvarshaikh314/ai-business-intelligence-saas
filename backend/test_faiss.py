# test_faiss.py
from app.services.rag_service import RAGService

# REPLACE THESE WITH THE REAL IDs FROM YOUR DATABASE
DATASET_ID = "YOUR-ACTUAL-PDF-ID-HERE" 
USER_ID = "YOUR-ACTUAL-USER-ID-HERE"

query = "list my top skills"
retrieved = RAGService.retrieve(DATASET_ID, USER_ID, query, top_k=5)

chunks = retrieved.get("chunks", [])
scores = retrieved.get("scores", [])

print(f"\nFound {len(chunks)} chunks.")
print("-" * 50)
for i, (chunk, score) in enumerate(zip(chunks, scores)):
    print(f"\n--- Chunk {i+1} (Score: {score}) ---")
    print(chunk)