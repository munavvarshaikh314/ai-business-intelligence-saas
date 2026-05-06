"use client";

import { useState } from "react";
import { updatePreferences } from "@/lib/settingsApi";

export default function PreferencesForm() {
  const [language, setLanguage] = useState("en");
  const [region, setRegion] = useState("India");

  const [loading, setLoading] = useState(false);
  const [msg, setMsg] = useState("");

  const handleSave = async (e) => {
    e.preventDefault();
    setLoading(true);
    setMsg("");

    try {
      await updatePreferences({ language, region });
      setMsg("Preferences updated successfully.");
    } catch (err) {
      setMsg("Failed to update preferences.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-lg font-bold text-slate-950">Preferences</h2>

      <label className="mb-1 block text-sm font-medium text-slate-700">Language</label>
      <select
        className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        value={language}
        onChange={(e) => setLanguage(e.target.value)}
      >
        <option value="en">English</option>
        <option value="hi">Hindi</option>
        <option value="ur">Urdu</option>
        <option value="ar">Arabic</option>
      </select>

      <label className="mb-1 block text-sm font-medium text-slate-700">Region</label>
      <select
        className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        value={region}
        onChange={(e) => setRegion(e.target.value)}
      >
        <option value="India">India</option>
        <option value="USA">USA</option>
        <option value="UAE">UAE</option>
        <option value="UK">UK</option>
      </select>

      <button
        disabled={loading}
        className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300"
      >
        {loading ? "Saving..." : "Save Preferences"}
      </button>

      {msg && <p className="mt-3 text-sm text-emerald-700">{msg}</p>}
    </form>
  );
}
