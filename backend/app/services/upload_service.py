import os
import shutil
import pandas as pd
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.models.document_chunk_model import DocumentChunk
from app.utils.chunk_utils import chunk_text
from app.utils.faiss_utils import save_faiss_index
from app.database import SessionLocal
from app.models.file_model import File
from app.models.dataset_model import Dataset
from app.models.dataset_column_model import DatasetColumn
from app.utils.sql_utils import sanitize_column_name, sanitize_table_name


UPLOAD_DIR = "app/storage/uploads"


class UploadService:

    def ensure_upload_dir():
        os.makedirs(UPLOAD_DIR, exist_ok=True)
    
    @staticmethod
    def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    # remove unnamed columns
        df = df.loc[:, ~df.columns.str.contains("^Unnamed")]

    # strip column names
        df.columns = [col.strip() for col in df.columns]

    # drop fully empty rows
        df = df.dropna(how="all")

    # clean values + convert numeric safely
        for col in df.columns:
            df[col] = df[col].astype(str).str.replace(",", "").str.replace("₹", "").str.strip()
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # fill remaining NaNs
            df = df.fillna("")

            return df

    def infer_sql_type(series: pd.Series) -> str:
        if pd.api.types.is_integer_dtype(series):
            return "INTEGER"
        if pd.api.types.is_float_dtype(series):
            return "FLOAT"
        if pd.api.types.is_bool_dtype(series):
            return "BOOLEAN"
        if pd.api.types.is_datetime64_any_dtype(series):
            return "TIMESTAMP"
        return "TEXT"

    @staticmethod
    def drop_table_if_exists(db: Session, table_name: str):
        query = text(f'DROP TABLE IF EXISTS "{table_name}" CASCADE')
        db.execute(query)
        db.commit()

    @staticmethod
    def create_table_from_dataframe(db: Session, table_name: str, df: pd.DataFrame):
        columns_sql = []

        for col in df.columns:
            safe_col = sanitize_column_name(col)
            sql_type = UploadService.infer_sql_type(df[col])
            columns_sql.append(f'"{safe_col}" {sql_type}')

        create_query = text(f'CREATE TABLE "{table_name}" ({", ".join(columns_sql)})')
        db.execute(create_query)
        db.commit()

    @staticmethod
    def insert_dataframe_into_table(db: Session, table_name: str, df: pd.DataFrame):
        safe_cols = [sanitize_column_name(c) for c in df.columns]

        for _, row in df.iterrows():
            values = []
            for value in row.tolist():
                if value == "":
                    values.append("NULL")
                else:
                    values.append("'" + str(value).replace("'", "''") + "'")

            column_names = ", ".join([f'"{c}"' for c in safe_cols])
            insert_query = text(
                f'INSERT INTO "{table_name}" ({column_names}) VALUES ({", ".join(values)})'
            )

            db.execute(insert_query)

        db.commit()

    @staticmethod
    def build_pdf_faiss_index(dataset_id: str, user_id: str, file_path: str, file_id: str = None):
        db: Session = SessionLocal()
        file_record = None
        try:
            if file_id:
                file_record = db.query(File).filter(
                    File.id == file_id,
                    File.dataset_id == dataset_id,
                    File.user_id == user_id,
                ).first()
            else:
                file_record = db.query(File).filter(
                    File.dataset_id == dataset_id,
                    File.user_id == user_id,
                    File.file_type == "pdf",
                    File.file_path == file_path,
                ).order_by(File.uploaded_at.desc()).first()

            if not file_record:
                raise Exception("Uploaded PDF file record not found")

            # delete old chunks if reindexing
            db.query(DocumentChunk).filter(DocumentChunk.dataset_id == dataset_id).delete()
            db.commit()

            reader = PdfReader(file_path)

            all_chunks = []
            chunk_metadata = []
            chunk_counter = 0

            for page_no, page in enumerate(reader.pages):
                page_text = page.extract_text()
                if not page_text:
                    continue

                chunks = chunk_text(page_text, chunk_size=700, overlap=150)

                for _, chunk in chunks:
                    all_chunks.append(chunk)

                    chunk_metadata.append({
                        "chunk_index": chunk_counter, "page_number": page_no + 1, "content": chunk})

                    chunk_obj = DocumentChunk(
                        dataset_id=dataset_id,
                        file_id=file_record.id,
                        content=chunk,
                        chunk_index=chunk_counter,
                    )

                    db.add(chunk_obj)
                    chunk_counter += 1

            db.commit()

            if not all_chunks:
                raise Exception("No readable text found in PDF")

            model = SentenceTransformer("all-MiniLM-L6-v2")
            embeddings = model.encode(all_chunks, show_progress_bar=True)

            embeddings = np.array(embeddings).astype("float32")

            dimension = embeddings.shape[1]
            index = faiss.IndexFlatL2(dimension)
            index.add(embeddings)

            save_faiss_index(dataset_id, index, chunk_metadata)

            return True
        finally:
            db.close()

    @staticmethod
    async def upload_csv(dataset_id: str, user_id: str, file: UploadFile):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        if not file.filename.endswith(".csv"):
            raise HTTPException(status_code=400, detail="Only CSV files allowed")

        UploadService.ensure_upload_dir()

        # Save CSV file
        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Read CSV
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"CSV read failed: {str(e)}")

        if df.empty:
            raise HTTPException(status_code=400, detail="CSV file is empty")

        df = UploadService.clean_dataframe(df)

        # Create a unique SQL table name
        safe_base = sanitize_table_name(dataset.dataset_name)
        table_name = f"{safe_base}_{str(dataset.id).replace('-', '')[:8]}"

        # If dataset already has table, drop it first (re-upload case)
        if dataset.table_name:
            UploadService.drop_table_if_exists(db, dataset.table_name)

        # Create SQL table
        UploadService.create_table_from_dataframe(db, table_name, df)

        # Insert all rows
        UploadService.insert_dataframe_into_table(db, table_name, df)

        # Save file record
        new_file = File(
            user_id=user_id,
            dataset_id=dataset_id,
            file_name=file.filename,
            file_type="csv",
            file_path=file_path,
            file_size=os.path.getsize(file_path)
        )
        db.add(new_file)

        # Update dataset metadata
        dataset.row_count = df.shape[0]
        dataset.column_count = df.shape[1]
        dataset.table_name = table_name

        # Delete old dataset_columns if reuploading
        db.query(DatasetColumn).filter(DatasetColumn.dataset_id == dataset_id).delete()

        # Save dataset columns schema
        for col in df.columns:
            safe_col = sanitize_column_name(col)
            sql_type = UploadService.infer_sql_type(df[col])

            column_obj = DatasetColumn(
                dataset_id=dataset_id,
                column_name=safe_col,
                data_type=sql_type,
                is_nullable=True
            )
            db.add(column_obj)

        db.commit()
        
        # Auto-train ML model in background

        try:
            from app.services.ml_model_service import MLModelService
            import threading
            thread = threading.Thread(
                target=MLModelService.auto_train,
                args=(user_id, dataset_id, file_path),
                daemon=True
            )
            thread.start()
        except Exception:
            pass  # Auto-train failure never blocks upload

        return {
            "message": "CSV uploaded successfully and SQL table created",
            "rows": dataset.row_count,
            "columns": dataset.column_count,
            "table_name": dataset.table_name
        }

    @staticmethod
    async def upload_pdf(dataset_id: str, user_id: str, file: UploadFile):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
            Dataset.id == dataset_id,
            Dataset.user_id == user_id
        ).first()

        if not dataset:
            raise HTTPException(status_code=404, detail="Dataset not found")

        if not file.filename.endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files allowed")

        UploadService.ensure_upload_dir()

        file_path = os.path.join(UPLOAD_DIR, file.filename)

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Save file record
        new_file = File(
            user_id=user_id,
            dataset_id=dataset_id,
            file_name=file.filename,
            file_type="pdf",
            file_path=file_path,
            file_size=os.path.getsize(file_path)
        )
        db.add(new_file)
        db.commit()
        db.refresh(new_file)

        # ---------------------------
        # Extract PDF text page-wise
        # ---------------------------
        reader = PdfReader(file_path)

        all_chunks = []
        chunk_metadata = []

        chunk_counter = 0

        for page_no, page in enumerate(reader.pages):
            page_text = page.extract_text()

            if not page_text:
                continue

            chunks = chunk_text(page_text, chunk_size=700, overlap=150)

            # for idx, chunk in chunks:
            for chunk in chunks:
                all_chunks.append(chunk)

                chunk_metadata.append({
                    "chunk_index": chunk_counter,
                    "page_number": page_no + 1,
                    "content": chunk  # ← required for RAG retrieval
                })

                # Save chunk into DB
                chunk_obj = DocumentChunk(
                    dataset_id=dataset_id,
                    file_id=new_file.id,
                    content=chunk,
                    chunk_index=chunk_counter,
                )

                db.add(chunk_obj)
                chunk_counter += 1

        db.commit()

        if not all_chunks:
            raise HTTPException(status_code=400, detail="No readable text found in PDF")

        # ---------------------------
        # Create embeddings + FAISS index
        # ---------------------------
        model = SentenceTransformer("all-MiniLM-L6-v2")

        embeddings = model.encode(all_chunks, show_progress_bar=True)

        embeddings = np.array(embeddings).astype("float32")

        dimension = embeddings.shape[1]

        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)

        save_faiss_index(dataset_id, index, chunk_metadata)

        return {
            "message": "PDF uploaded and indexed successfully",
            "chunks": len(all_chunks)
        }

    @staticmethod
    async def save_pdf_file_only(dataset_id: str, user_id: str, file: UploadFile):
        db: Session = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            if not file.filename.endswith(".pdf"):
                raise HTTPException(status_code=400, detail="Only PDF files allowed")

            UploadService.ensure_upload_dir()

            file_path = os.path.join(UPLOAD_DIR, file.filename)

            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)

            new_file = File(
                user_id=user_id,
                dataset_id=dataset_id,
                file_name=file.filename,
                file_type="pdf",
                file_path=file_path,
                file_size=os.path.getsize(file_path)
            )

            db.add(new_file)

            dataset.index_status = "QUEUED"
            dataset.index_progress = 0

            db.commit()

            db.refresh(new_file)
            return {"file_path": file_path, "file_id": str(new_file.id)}
        finally:
            db.close()

    @staticmethod
    def get_upload_status(dataset_id: str, user_id: str):
        db: Session = SessionLocal()

        dataset = db.query(Dataset).filter(
        Dataset.id == dataset_id,
        Dataset.user_id == user_id
        ).first()

        if not dataset:
         raise HTTPException(status_code=404, detail="Dataset not found")

        return {
        "dataset_id": dataset.id,
        "status": dataset.index_status,
        "progress": dataset.index_progress
    }

