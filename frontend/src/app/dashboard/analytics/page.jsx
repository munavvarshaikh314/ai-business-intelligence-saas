"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { AlertCircle, UploadCloud } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useDataset } from "@/context/DatasetContext";
import StatsCards from "@/components/dashboard/StatsCards";
import SalesTrendChart from "@/components/charts/SalesTrendChart";
import CategoryPieChart from "@/components/charts/CategoryPieChart";
import RegionBarChart from "@/components/charts/RegionBarChart";
import {
  fetchSummary,
  fetchSalesTrend,
  fetchCategoryBreakdown,
  fetchRegionBreakdown,
} from "@/lib/analyticsApi";

export default function AnalyticsPage() {
  const { user, loading } = useAuth();
  const { activeDataset } = useDataset();
  const router = useRouter();

  const [summary, setSummary] = useState(null);
  const [trend, setTrend] = useState([]);
  const [categories, setCategories] = useState([]);
  const [regions, setRegions] = useState([]);
  const [error, setError] = useState("");
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  useEffect(() => {
    const loadAnalytics = async () => {
      if (!activeDataset) return;

      setLoadingAnalytics(true);
      setError("");

      try {
        const [summaryData, trendData, catData, regionData] = await Promise.all([
          fetchSummary(activeDataset.id),
          fetchSalesTrend(activeDataset.id),
          fetchCategoryBreakdown(activeDataset.id),
          fetchRegionBreakdown(activeDataset.id),
        ]);

        setSummary(summaryData);
        setTrend(Array.isArray(trendData) ? trendData : []);
        setCategories(Array.isArray(catData) ? catData : []);
        setRegions(Array.isArray(regionData) ? regionData : []);
      } catch (err) {
        setSummary(null);
        setTrend([]);
        setCategories([]);
        setRegions([]);
        setError(err?.response?.data?.detail || "Upload a CSV file to this dataset before opening analytics.");
      } finally {
        setLoadingAnalytics(false);
      }
    };

    loadAnalytics();
  }, [activeDataset]);

  if (loading) return <p className="p-4">Loading...</p>;
  if (!user) return null;

  if (!activeDataset) {
    return (
      <EmptyState
        title="No dataset selected"
        message="Create or select a dataset, then upload a CSV file to unlock analytics."
      />
    );
  }

  const hasCharts = trend.length || categories.length || regions.length;

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Analytics</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">{activeDataset.dataset_name}</h1>
        <p className="mt-2 text-sm text-slate-500">
          CSV dashboards are generated from the uploaded table. PDF datasets are available in chatbot/RAG.
        </p>
      </section>

      {loadingAnalytics ? (
        <p className="rounded-lg border border-slate-200 bg-white p-5 text-sm text-slate-500 shadow-sm">Loading analytics...</p>
      ) : error ? (
        <EmptyState title="Analytics not ready" message={error} />
      ) : (
        <>
          <StatsCards summary={summary} />
          {!hasCharts && (
            <div className="rounded-lg border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">
              Charts need recognizable columns such as date, revenue/sales/amount, region/city, or category/product.
            </div>
          )}
          <div className="grid gap-6 xl:grid-cols-2">
            <SalesTrendChart data={trend} />
            <CategoryPieChart data={categories} />
          </div>
          <RegionBarChart data={regions} />
        </>
      )}
    </div>
  );
}

function EmptyState({ title, message }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-8 text-center shadow-sm">
      <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-md bg-amber-50 text-amber-700">
        <AlertCircle size={24} />
      </div>
      <h2 className="text-xl font-bold text-slate-950">{title}</h2>
      <p className="mx-auto mt-2 max-w-xl text-sm leading-6 text-slate-500">{message}</p>
      <Link
        href="/dashboard/upload"
        className="mt-5 inline-flex items-center gap-2 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700"
      >
        <UploadCloud size={16} />
        Upload CSV
      </Link>
    </div>
  );
}
