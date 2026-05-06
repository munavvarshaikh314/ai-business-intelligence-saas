"use client";

import Link from "next/link";
import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { BarChart3, Bot, CreditCard, UploadCloud } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { useDataset } from "@/context/DatasetContext";
import { useCredits } from "@/context/CreditsContext";
import CreateDatasetForm from "@/components/dashboard/CreateDatasetForm";

const actions = [
  {
    title: "Upload Data",
    description: "Add CSV or PDF files for analytics and retrieval.",
    href: "/dashboard/upload",
    icon: UploadCloud,
  },
  {
    title: "Analytics",
    description: "Review KPIs, trends, and dataset breakdowns.",
    href: "/dashboard/analytics",
    icon: BarChart3,
  },
  {
    title: "AI Chatbot",
    description: "Ask questions with RAG, SQL, and prediction routing.",
    href: "/dashboard/chatbot",
    icon: Bot,
  },
  {
    title: "Billing",
    description: "Buy credits and review payment history.",
    href: "/dashboard/billing",
    icon: CreditCard,
  },
];

export default function DashboardPage() {
  const { user, loading } = useAuth();
  const { datasets, activeDataset } = useDataset();
  const { credits } = useCredits();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading) return <p>Loading...</p>;
  if (!user) return null;

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <div className="flex flex-col gap-5 md:flex-row md:items-end md:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Workspace</p>
            <h1 className="mt-2 text-3xl font-bold text-slate-950">Welcome back, {user.name}</h1>
            <p className="mt-2 text-sm text-slate-500">
              Active dataset: <span className="font-semibold text-slate-800">{activeDataset?.dataset_name || "None selected"}</span>
            </p>
          </div>
          <div className="grid grid-cols-2 gap-3 text-sm">
            <div className="rounded-md border border-slate-200 px-4 py-3">
              <p className="text-slate-500">Datasets</p>
              <p className="text-2xl font-bold text-slate-950">{datasets.length}</p>
            </div>
            <div className="rounded-md border border-slate-200 px-4 py-3">
              <p className="text-slate-500">Credits</p>
              <p className="text-2xl font-bold text-slate-950">{credits}</p>
            </div>
          </div>
        </div>
      </section>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <section className="grid gap-4 md:grid-cols-2">
          {actions.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.href}
                href={item.href}
                className="group rounded-lg border border-slate-200 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:border-emerald-300 hover:shadow-md"
              >
                <div className="mb-4 flex h-10 w-10 items-center justify-center rounded-md bg-slate-950 text-white group-hover:bg-emerald-700">
                  <Icon size={20} />
                </div>
                <h2 className="font-bold text-slate-950">{item.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500">{item.description}</p>
              </Link>
            );
          })}
        </section>

        <CreateDatasetForm />
      </div>
    </div>
  );
}
