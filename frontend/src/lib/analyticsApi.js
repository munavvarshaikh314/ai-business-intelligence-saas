import api from "@/lib/api";

export const fetchSummary = async (datasetId) => {
  const res = await api.get(`/analytics/summary/${datasetId}`);
  return res.data;
};

export const fetchSalesTrend = async (datasetId) => {
  const res = await api.get(`/analytics/sales-trend/${datasetId}`);
  return res.data;
};

export const fetchCategoryBreakdown = async (datasetId) => {
  const res = await api.get(`/analytics/category-breakdown/${datasetId}`);
  return res.data;
};

export const fetchRegionBreakdown = async (datasetId) => {
  const res = await api.get(`/analytics/region-breakdown/${datasetId}`);
  return res.data;
};