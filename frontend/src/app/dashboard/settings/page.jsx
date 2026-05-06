"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { LogOut } from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import ProfileForm from "@/components/settings/ProfileForm";
import PreferencesForm from "@/components/settings/PreferencesForm";
import PasswordForm from "@/components/settings/PasswordForm";

export default function SettingsPage() {
  const { user, loading, logout } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.push("/login");
  }, [user, loading, router]);

  if (loading) return <p className="p-4">Loading...</p>;
  if (!user) return null;

  return (
    <div className="space-y-6">
      <section className="flex flex-col gap-4 rounded-lg border border-slate-200 bg-white p-6 shadow-sm md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm font-semibold uppercase tracking-wide text-emerald-600">Account</p>
          <h1 className="mt-2 text-3xl font-bold text-slate-950">Settings</h1>
          <p className="mt-2 text-sm text-slate-500">Manage profile, preferences, and password.</p>
        </div>
        <button
          onClick={logout}
          className="inline-flex items-center justify-center gap-2 rounded-md border border-red-200 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-50"
        >
          <LogOut size={16} />
          Logout
        </button>
      </section>

      <div className="grid gap-6 xl:grid-cols-2">
        <ProfileForm />
        <PreferencesForm />
      </div>

      <div className="max-w-xl">
        <PasswordForm />
      </div>
    </div>
  );
}
