"use client";

import { useState } from "react";
import { changePassword } from "@/lib/settingsApi";

export default function PasswordForm() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");

  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  const handleChange = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMsg("");

    try {
      await changePassword({ old_password: oldPassword, new_password: newPassword });
      setMsg("Password updated successfully.");
      setOldPassword("");
      setNewPassword("");
    } catch (err) {
      setMsg("Failed to update password.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleChange} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-lg font-bold text-slate-950">Change Password</h2>

      <label className="mb-1 block text-sm font-medium text-slate-700">Old Password</label>
      <input
        className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        type="password"
        value={oldPassword}
        onChange={(e) => setOldPassword(e.target.value)}
      />

      <label className="mb-1 block text-sm font-medium text-slate-700">New Password</label>
      <input
        className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        type="password"
        value={newPassword}
        onChange={(e) => setNewPassword(e.target.value)}
      />

      <button
        disabled={loading}
        className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300"
      >
        {loading ? "Updating..." : "Update Password"}
      </button>

      {msg && <p className="mt-3 text-sm text-emerald-700">{msg}</p>}
    </form>
  );
}
