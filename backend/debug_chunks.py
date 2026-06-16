# Quick debug script — paste into your terminal to check what chunk_obj looks like
# Run: python3 debug_chunks.py

import sys
sys.path.insert(0, ".")

from app.database import SessionLocal
from app.models.document_chunk_model import DocumentChunk

db = SessionLocal()
chunk = db.query(DocumentChunk).first()
if chunk:
    print("Chunk fields:", [c.name for c in chunk.__table__.columns])
    print("chunk_text:", getattr(chunk, "chunk_text", "NOT FOUND"))
    print("content:", getattr(chunk, "content", "NOT FOUND"))
    print("text:", getattr(chunk, "text", "NOT FOUND"))
else:
    print("No chunks found in DB")
db.close()