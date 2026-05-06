"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { FileText, Table2 } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useDataset } from "@/context/DatasetContext";
import UploadCSV from "@/components/upload/UploadCSV";
import UploadPDF from "@/components/upload/UploadPDF";
import CreateDatasetForm from "@/components/dashboard/CreateDatasetForm";

export default function UploadPage() {
  const { user, loading } = useAuth();
  const { activeDataset } = useDataset();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading) return <p className="p-4">Loading...</p>;
  if (!user) return null;

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Upload Center</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">
          {activeDataset ? activeDataset.dataset_name : "Create a dataset first"}
        </h1>
        <p className="mt-2 text-sm text-slate-500">
          CSV files power analytics and SQL chat. PDF files power RAG document Q&A.
        </p>
      </section>

      {!activeDataset && (
        <div className="max-w-xl">
          <CreateDatasetForm />
        </div>
      )}

      {activeDataset && (
        <div className="grid gap-6 xl:grid-cols-2">
          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-emerald-50 text-emerald-700">
                <Table2 size={20} />
              </div>
              <div>
                <h2 className="font-bold text-slate-950">Analytics Dataset</h2>
                <p className="text-sm text-slate-500">Upload CSV for dashboards and SQL answers.</p>
              </div>
            </div>
            <UploadCSV />
          </div>

          <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
            <div className="mb-4 flex items-center gap-3">
              <div className="flex h-10 w-10 items-center justify-center rounded-md bg-blue-50 text-blue-700">
                <FileText size={20} />
              </div>
              <div>
                <h2 className="font-bold text-slate-950">Document Dataset</h2>
                <p className="text-sm text-slate-500">Upload PDF for RAG/chatbot answers.</p>
              </div>
            </div>
            <UploadPDF />
          </div>
        </div>
      )}
    </div>
  );
}
