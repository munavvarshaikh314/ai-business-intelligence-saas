from fastapi import APIRouter, Depends
from app.dependencies import get_current_user
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics_schema import SQLQueryRequest

router = APIRouter()

@router.get("/summary/{dataset_id}")
def get_summary(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_summary(dataset_id, current_user.id)

@router.get("/columns/{dataset_id}")
def get_column_stats(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_column_statistics(dataset_id, current_user.id)

@router.get("/monthly-sales/{dataset_id}")
def get_monthly_sales(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_monthly_sales(dataset_id, current_user.id)

@router.get("/sales-trend/{dataset_id}")
def get_sales_trend(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_monthly_sales(dataset_id, current_user.id)

@router.get("/region-sales/{dataset_id}")
def get_region_sales(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_region_sales(dataset_id, current_user.id)

@router.get("/region-breakdown/{dataset_id}")
def get_region_breakdown(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_region_sales(dataset_id, current_user.id)

@router.get("/category-sales/{dataset_id}")
def get_category_sales(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_category_sales(dataset_id, current_user.id)

@router.get("/category-breakdown/{dataset_id}")
def get_category_breakdown(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_category_sales(dataset_id, current_user.id)

@router.get("/profit-trend/{dataset_id}")
def get_profit_trend(dataset_id: str, current_user=Depends(get_current_user)):
    return AnalyticsService.get_profit_trend(dataset_id, current_user.id)

@router.post("/sql/{dataset_id}")
def run_sql_query(dataset_id: str, payload: SQLQueryRequest, current_user=Depends(get_current_user)):
    return AnalyticsService.run_sql(dataset_id, current_user.id, payload.sql)
