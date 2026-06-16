"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/context/AuthContext";
import {
  bootstrapFirstAdmin,
  fetchAdminBootstrapStatus,
  fetchAllUsers,
  fetchAllPayments,
  fetchUsageLogs,
} from "@/lib/adminApi";

import AdminUsersTable from "@/components/admin/AdminUsersTable";
import AdminPaymentsTable from "@/components/admin/AdminPaymentsTable";
import AdminUsageLogsTable from "@/components/admin/AdminUsageLogsTable";

export default function AdminPage() {
  const { user, loading, refreshUser } = useAuth();
  const router = useRouter();

  const [tab, setTab] = useState("users");
  const [adminExists, setAdminExists] = useState(true);
  const [bootstrapping, setBootstrapping] = useState(false);

  const [users, setUsers] = useState([]);
  const [payments, setPayments] = useState([]);
  const [logs, setLogs] = useState([]);

  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  useEffect(() => {
    const loadBootstrapStatus = async () => {
      if (!user || (user.role || "").toLowerCase() === "admin") return;

      try {
        const status = await fetchAdminBootstrapStatus();
        setAdminExists(status.admin_exists);
      } catch {
        setAdminExists(true);
      }
    };

    loadBootstrapStatus();
  }, [user]);

  const loadUsers = async () => {
    const data = await fetchAllUsers();
    setUsers(data);
  };

  const loadPayments = async () => {
    const data = await fetchAllPayments();
    setPayments(data);
  };

  const loadLogs = async () => {
    const data = await fetchUsageLogs();
    setLogs(data);
  };

  useEffect(() => {
    const loadData = async () => {
      if (!user || (user.role || "").toLowerCase() !== "admin") return;

      setError("");

      try {
        if (tab === "users") await loadUsers();
        if (tab === "payments") await loadPayments();
        if (tab === "logs") await loadLogs();
      } catch (err) {
        setError(err?.response?.data?.detail || "Failed to load admin data");
      }
    };

    loadData();
  }, [tab, user]);

  const handleBootstrap = async () => {
    setBootstrapping(true);
    setError("");

    try {
      await bootstrapFirstAdmin();
      await refreshUser?.();
      setAdminExists(true);
    } catch (err) {
      setError(err?.response?.data?.detail || "Could not create first admin");
    } finally {
      setBootstrapping(false);
    }
  };

  if (loading) return <p>Loading...</p>;
  if (!user) return null;

  const isAdmin = (user.role || "").toLowerCase() === "admin";

  if (!isAdmin) {
    return (
      <div className="space-y-6">
        <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          <p className="text-sm font-semibold uppercase tracking-wide text-amber-600">Admin Access</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">Admin account required</h1>
          <p className="mt-2 text-sm leading-6 text-slate-500">
            You are signed in as <span className="font-semibold text-slate-800">{user.email}</span> with role{" "}
            <span className="font-semibold text-slate-800">{user.role || "unknown"}</span>.
          </p>
        </section>

        <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
          {!adminExists ? (
            <>
              <h2 className="text-xl font-bold text-slate-950">No admin exists yet</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                This looks like a fresh project database. You can promote your current account as the first admin.
              </p>
              <button
                onClick={handleBootstrap}
                disabled={bootstrapping}
                className="mt-5 rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300"
              >
                {bootstrapping ? "Creating admin..." : "Make me first admin"}
              </button>
            </>
          ) : (
            <>
              <h2 className="text-xl font-bold text-slate-950">You are not an admin</h2>
              <p className="mt-2 text-sm leading-6 text-slate-500">
                Ask an existing admin to promote your account, or update your user role in the database to admin.
              </p>
            </>
          )}

          {error && <p className="mt-4 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <section className="rounded-lg border border-slate-200 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Admin</p>
        <h1 className="mt-2 text-3xl font-bold text-slate-950">Control Panel</h1>
        <p className="mt-2 text-sm text-slate-500">Manage users, credits, payments, and usage logs.</p>
      </section>

      {error && <p className="rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</p>}

      <div className="flex gap-3">
        <button
          onClick={() => setTab("users")}
          className={`rounded-md px-4 py-2 text-sm font-semibold transition ${
            tab === "users" ? "bg-slate-950 text-white" : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          Users
        </button>

        <button
          onClick={() => setTab("payments")}
          className={`rounded-md px-4 py-2 text-sm font-semibold transition ${
            tab === "payments" ? "bg-slate-950 text-white" : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          Payments
        </button>

        <button
          onClick={() => setTab("logs")}
          className={`rounded-md px-4 py-2 text-sm font-semibold transition ${
            tab === "logs" ? "bg-slate-950 text-white" : "border border-slate-200 bg-white text-slate-700 hover:bg-slate-50"
          }`}
        >
          Usage Logs
        </button>
      </div>

      {tab === "users" && (
        <AdminUsersTable users={users} onRefresh={loadUsers} />
      )}

      {tab === "payments" && <AdminPaymentsTable payments={payments} />}

      {tab === "logs" && <AdminUsageLogsTable logs={logs} />}
    </div>
  );
}
