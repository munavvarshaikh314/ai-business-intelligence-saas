"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";

import { useAuth } from "@/context/AuthContext";
import {
  fetchAllUsers,
  fetchAllPayments,
  fetchUsageLogs,
} from "@/lib/adminApi";

import AdminUsersTable from "@/components/admin/AdminUsersTable";
import AdminPaymentsTable from "@/components/admin/AdminPaymentsTable";
import AdminUsageLogsTable from "@/components/admin/AdminUsageLogsTable";

export default function AdminPage() {
  const { user, loading } = useAuth();
  const router = useRouter();

  const [tab, setTab] = useState("users");

  const [users, setUsers] = useState([]);
  const [payments, setPayments] = useState([]);
  const [logs, setLogs] = useState([]);

  const [error, setError] = useState("");

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading]);

  // simple admin check
  useEffect(() => {
    if (user && user.role !== "admin") {
      router.push("/dashboard");
    }
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
      setError("");

      try {
        if (tab === "users") await loadUsers();
        if (tab === "payments") await loadPayments();
        if (tab === "logs") await loadLogs();
      } catch (err) {
        setError("Failed to load admin data");
      }
    };

    loadData();
  }, [tab]);

  if (loading) return <p>Loading...</p>;
  if (!user) return null;

  return (
    <div>
      <h1 className="text-2xl font-bold mb-4">Admin Panel</h1>

      {error && <p className="text-red-600 mb-3">{error}</p>}

      <div className="flex gap-3 mb-6">
        <button
          onClick={() => setTab("users")}
          className={`px-4 py-2 rounded ${
            tab === "users" ? "bg-black text-white" : "bg-white border"
          }`}
        >
          Users
        </button>

        <button
          onClick={() => setTab("payments")}
          className={`px-4 py-2 rounded ${
            tab === "payments" ? "bg-black text-white" : "bg-white border"
          }`}
        >
          Payments
        </button>

        <button
          onClick={() => setTab("logs")}
          className={`px-4 py-2 rounded ${
            tab === "logs" ? "bg-black text-white" : "bg-white border"
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