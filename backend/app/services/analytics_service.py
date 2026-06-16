import pandas as pd
from fastapi import HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.database import SessionLocal
from app.models.dataset_model import Dataset
from app.models.dataset_row_model import DatasetRow
from app.utils.sql_utils import is_safe_select_query


class AnalyticsService:

    @staticmethod
    def get_dataset_table(dataset_id: str, user_id: str) -> str:
        db: Session = SessionLocal()
        try:
            dataset = db.query(Dataset).filter(
                Dataset.id == dataset_id,
                Dataset.user_id == user_id
            ).first()

            if not dataset:
                raise HTTPException(status_code=404, detail="Dataset not found")

            if not dataset.table_name:
                raise HTTPException(
                    status_code=400,
                    detail="Upload a CSV file to this dataset before opening analytics."
                )

            return dataset.table_name

        finally:
            db.close()

    @staticmethod
    def get_columns(db: Session, table_name: str):
        rows = db.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position
        """), {"table_name": table_name}).fetchall()

        return [row[0] for row in rows]

    @staticmethod
    def first_matching_column(columns, candidates):
        normalized = {col.lower(): col for col in columns}

        for candidate in candidates:
            if candidate in normalized:
                return normalized[candidate]

        for col in columns:
            col_l = col.lower()
            if any(candidate in col_l for candidate in candidates):
                return col

        return None

    @staticmethod
    def _safe_numeric_expr(col_name: str) -> str:
         return f"""
        NULLIF(
            REGEXP_REPLACE(
                TRIM(REPLACE(REPLACE(CAST("{col_name}" AS TEXT), ',', ''), '₹', '')),
                '[^0-9.-]',
                '',
                'g'
            ),
            ''
        )::DOUBLE PRECISION
    """

    @staticmethod
    def _is_numeric_column(db: Session, table_name: str, col: str) -> bool:
        try:
            expr = AnalyticsService._safe_numeric_expr(col)

            q = text(f"""
                SELECT {expr} AS num_val
                FROM "{table_name}"
                WHERE "{col}" IS NOT NULL
                LIMIT 10
            """)

            rows = db.execute(q).fetchall()

            for r in rows:
                if r[0] is not None:
                    return True

            return False

        except Exception as e:
            print("NUMERIC CHECK FAILED:", col, str(e))
            db.rollback()
            return False

    @staticmethod
    def _find_best_column(db: Session, table_name: str, columns: list, keywords: list):
        candidates = []

        for col in columns:
           col_l = col.lower()
           if any(k in col_l for k in keywords):
            candidates.append(col)
        print("CANDIDATES:", candidates)    

        

        for col in candidates:
         if AnalyticsService._is_numeric_column(db, table_name, col):
            return col
        return None

    @staticmethod
    def get_summary(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            table_name = AnalyticsService.get_dataset_table(dataset_id, user_id)

            total_rows = db.execute(
                text(f'SELECT COUNT(*) FROM "{table_name}"')
            ).scalar() or 0

            columns = AnalyticsService.get_columns(db, table_name)

            revenue_col = AnalyticsService._find_best_column(
                db, table_name, columns,
                ["revenue", "amount", "price", "sales", "total", "order_value"]
            )

            profit_col = AnalyticsService._find_best_column(
                db, table_name, columns,
                ["profit", "net_profit", "margin"]
            )

            order_col = AnalyticsService.first_matching_column(
                columns,
                ["order_id", "order", "invoice", "bill", "transaction_id", "id"]
            )

            total_revenue = None
            avg_order_value = None
            total_profit = None

            # ---------- Revenue ----------
            if revenue_col:
                try:
                    revenue_expr = AnalyticsService._safe_numeric_expr(revenue_col)

                    total_revenue = db.execute(
                        text(f'SELECT SUM({revenue_expr}) FROM "{table_name}"')
                    ).scalar()

                    avg_order_value = db.execute(
                        text(f'SELECT AVG({revenue_expr}) FROM "{table_name}"')
                    ).scalar()

                except Exception:
                    db.rollback()
                    total_revenue = None
                    avg_order_value = None

            # ---------- Profit ----------
            if profit_col:
                try:
                    profit_expr = AnalyticsService._safe_numeric_expr(profit_col)

                    total_profit = db.execute(
                        text(f'SELECT SUM({profit_expr}) FROM "{table_name}"')
                    ).scalar()

                except Exception:
                    db.rollback()
                    total_profit = None

            # ---------- Orders ----------
            total_orders = total_rows
            if order_col:
                try:
                    total_orders = db.execute(
                        text(f'SELECT COUNT(DISTINCT "{order_col}") FROM "{table_name}"')
                    ).scalar() or total_rows

                except Exception:
                    db.rollback()
                    total_orders = total_rows
                    
                    print("COLUMNS:", columns)
                    print("REVENUE_COL:", revenue_col)
                    print("PROFIT_COL:", profit_col)
                    print("ORDER_COL:", order_col)

            return {
                "total_rows": int(total_rows),
                "total_orders": int(total_orders),
                "total_revenue": float(total_revenue) if total_revenue is not None else None,
                "total_profit": float(total_profit) if total_profit is not None else None,
                "avg_order_value": float(avg_order_value) if avg_order_value is not None else None,
                "table_name": table_name,
                "revenue_column": revenue_col,
                "profit_column": profit_col,
                "order_column": order_col,
            }

        finally:
            db.close()
    # ---------------------------
    # Column Statistics
    # ---------------------------
    @staticmethod
    def get_column_statistics(dataset_id: str, user_id: str):
        df = AnalyticsService.load_dataset_dataframe(dataset_id, user_id)

        stats = []

        for col in df.columns:
            null_count = int(df[col].isnull().sum())
            unique_count = int(df[col].nunique())

            col_info = {
                "column": col,
                "null_count": null_count,
                "unique_count": unique_count,
                "dtype": str(df[col].dtype)
            }

            # If numeric -> compute numeric stats
            if pd.api.types.is_numeric_dtype(df[col]):
                col_info["min"] = float(df[col].min(skipna=True))
                col_info["max"] = float(df[col].max(skipna=True))
                col_info["mean"] = float(df[col].mean(skipna=True))
                col_info["median"] = float(df[col].median(skipna=True))

            stats.append(col_info)

        return {"columns": stats}

    # ---------------------------
    # Monthly Sales Chart
    # Requires: date column + revenue column
    # ---------------------------
    @staticmethod
    def get_monthly_sales(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            table_name = AnalyticsService.get_dataset_table(dataset_id, user_id)

            columns = AnalyticsService.get_columns(db, table_name)

            date_col = AnalyticsService.first_matching_column(
            columns,
            ["sale_date", "date", "order_date", "created_at", "timestamp"]
            )

            revenue_col = AnalyticsService._find_best_column(
            db, table_name, columns,
            ["revenue", "sales_amount", "sales", "amount", "price", "total"]
            )

            if not date_col or not revenue_col:
              return []

            revenue_expr = AnalyticsService._safe_numeric_expr(revenue_col)

            sql = text(f"""
            SELECT 
                TO_CHAR(date_trunc('month', CAST("{date_col}" AS DATE)), 'YYYY-MM') AS month,
                SUM({revenue_expr}) AS total_revenue
                FROM "{table_name}"
                WHERE "{date_col}" IS NOT NULL
                GROUP BY month
                ORDER BY month;
            """)

            result = db.execute(sql).fetchall()

            return [{"date": row[0], "sales": float(row[1] or 0)} for row in result]

        except Exception:
           db.rollback()
           return []

        finally:
         db.close()
    # ---------------------------
    # Region Sales (Bar Chart)
    # Requires: region/city + revenue
    # ---------------------------
    @staticmethod
    def get_region_sales(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        

        try:
            table_name = AnalyticsService.get_dataset_table(dataset_id, user_id)

            columns = AnalyticsService.get_columns(db, table_name)

            region_col = AnalyticsService.first_matching_column(
            columns,
            ["region", "city", "state", "country", "location"]
            )

            revenue_col = AnalyticsService._find_best_column(
            db, table_name, columns,
            ["revenue", "sales_amount", "sales", "amount", "price", "total"]
            )

            if not region_col or not revenue_col:
               return []

            revenue_expr = AnalyticsService._safe_numeric_expr(revenue_col)

            sql = text(f"""
                SELECT "{region_col}" AS region,
                   SUM({revenue_expr}) AS total_revenue
                FROM "{table_name}"
                GROUP BY "{region_col}"
                ORDER BY total_revenue DESC
                LIMIT 10;
            """)

            result = db.execute(sql).fetchall()

            return [{"region": str(row[0]), "sales": float(row[1] or 0)} for row in result]

        except Exception:
          db.rollback()
          return []

        finally:
          db.close()
    # ---------------------------
    # Category Distribution (Pie Chart)
    # Requires: category/product + revenue
    # ---------------------------
    @staticmethod
    def get_category_sales(dataset_id: str, user_id: str):
        db: Session = SessionLocal()
        try:
            table_name = AnalyticsService.get_dataset_table(dataset_id, user_id)

            columns = AnalyticsService.get_columns(db, table_name)

            category_col = AnalyticsService.first_matching_column(
            columns,
            ["category", "product_category", "product", "item", "type", "segment"]
            )

            revenue_col = AnalyticsService._find_best_column(
            db, table_name, columns,
            ["revenue", "sales_amount", "sales", "amount", "price", "total"]
           )

            if not category_col or not revenue_col:
              return []

            revenue_expr = AnalyticsService._safe_numeric_expr(revenue_col)

            sql = text(f"""
                SELECT "{category_col}" AS category,
                   SUM({revenue_expr}) AS total_revenue
                FROM "{table_name}"
                GROUP BY "{category_col}"
                ORDER BY total_revenue DESC
                LIMIT 8;
            """)

            result = db.execute(sql).fetchall()

            return [{"category": str(row[0]), "value": float(row[1] or 0)} for row in result]

        except Exception:
          db.rollback()
          return []

        finally:
         db.close()
    # ---------------------------
    # Profit Trend (Optional)
    # Requires: profit column + date
    # ---------------------------
    @staticmethod
    def get_profit_trend(dataset_id: str, user_id: str):
        df = AnalyticsService.load_dataset_dataframe(dataset_id, user_id)

        profit_candidates = ["profit", "net_profit", "margin"]
        profit_col = None

        for col in df.columns:
            if col.lower() in profit_candidates:
                profit_col = col
                break

        if not profit_col:
            raise HTTPException(status_code=400, detail="No profit column found in dataset")

        date_candidates = ["date", "order_date", "timestamp", "created_at"]
        date_col = None

        for col in df.columns:
            if col.lower() in date_candidates:
                date_col = col
                break

        if not date_col:
            raise HTTPException(status_code=400, detail="No date column found in dataset")

        df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
        df[profit_col] = pd.to_numeric(df[profit_col], errors="coerce")

        df = df.dropna(subset=[date_col])

        df["month"] = df[date_col].dt.to_period("M").astype(str)
        grouped = df.groupby("month")[profit_col].sum().reset_index()

        return {
            "chartType": "line",
            "x": grouped["month"].tolist(),
            "y": grouped[profit_col].tolist(),
            "insight": "Monthly profit trend."
        }

    # ---------------------------
    # Safe SQL Query Execution (basic)
    # ---------------------------
    @staticmethod
    def run_sql(dataset_id: str, user_id: str, sql: str):
        db: Session = SessionLocal()
        table_name = AnalyticsService.get_dataset_table(dataset_id, user_id)

        if not is_safe_select_query(sql):
            raise HTTPException(status_code=400, detail="Only safe SELECT queries are allowed")

        # Optional: enforce table_name presence
        if table_name not in sql:
            raise HTTPException(
                status_code=400,
                detail=f"Query must use your dataset table: {table_name}"
            )

        try:
            result = db.execute(text(sql))
            rows = result.fetchall()
            columns = list(result.keys())

            return {
                "columns": columns,
                "rows": [list(r) for r in rows]
            }

        except Exception as e:
            raise HTTPException(status_code=400, detail=f"SQL execution failed: {str(e)}")
