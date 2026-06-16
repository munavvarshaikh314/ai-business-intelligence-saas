"use client";

import { useState } from "react";
import { updateProfile } from "@/lib/settingsApi";
import { useAuth } from "@/context/AuthContext";
import { getErrorMessage } from "@/lib/errors";

export default function ProfileForm() {
  const { user, refreshUser } = useAuth();

  const [name, setName] = useState(user?.name || "");
  const [email] = useState(user?.email || "");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleSave = async (e) => {
    e.preventDefault();
    setSuccess("");
    setError("");

    if (!name.trim()) {
      setError("Name cannot be empty.");
      return;
    }

    setLoading(true);
    try {
      await updateProfile({ name: name.trim() });
      await refreshUser?.();
      setSuccess("Profile updated successfully.");
    } catch (err) {
      setError(getErrorMessage(err, "Failed to update profile. Please try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSave} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-lg font-bold text-slate-950">Profile</h2>

      {error && (
        <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}
      {success && (
        <div className="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">✓ {success}</div>
      )}

      <label className="mb-1 block text-sm font-medium text-slate-700">Full Name</label>
      <input
        className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        value={name}
        onChange={(e) => { setError(""); setName(e.target.value); }}
      />

      <label className="mb-1 block text-sm font-medium text-slate-700">Email</label>
      <input
        className="mb-4 w-full rounded-md border border-slate-200 bg-slate-50 p-2 text-slate-500"
        value={email}
        disabled
      />
      <p className="mb-3 text-xs text-slate-400">Email cannot be changed.</p>

      <button
        disabled={loading}
        className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
      >
        {loading ? "Saving..." : "Save Profile"}
      </button>
    </form>
  );
}


// "use client";

// import { useState } from "react";
// import { updateProfile } from "@/lib/settingsApi";
// import { useAuth } from "@/context/AuthContext";

// export default function ProfileForm() {
//   const { user, refreshUser } = useAuth();

//   const [name, setName] = useState(user?.name || "");
//   const [email] = useState(user?.email || "");

//   const [loading, setLoading] = useState(false);
//   const [msg, setMsg] = useState("");

//   const handleSave = async (e) => {
//     e.preventDefault();
//     setLoading(true);
//     setMsg("");

//     try {
//       await updateProfile({ name });
//       await refreshUser?.();
//       setMsg("Profile updated successfully.");
//     } catch (err) {
//       setMsg("Failed to update profile.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <form onSubmit={handleSave} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
//       <h2 className="mb-4 text-lg font-bold text-slate-950">Profile</h2>

//       <label className="mb-1 block text-sm font-medium text-slate-700">Full Name</label>
//       <input
//         className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
//         value={name}
//         onChange={(e) => setName(e.target.value)}
//       />

//       <label className="mb-1 block text-sm font-medium text-slate-700">Email</label>
//       <input
//         className="mb-3 w-full rounded-md border border-slate-200 bg-slate-50 p-2 text-slate-500"
//         value={email}
//         disabled
//       />

//       <button
//         disabled={loading}
//         className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300"
//       >
//         {loading ? "Saving..." : "Save Profile"}
//       </button>

//       {msg && <p className="mt-3 text-sm text-emerald-700">{msg}</p>}
//     </form>
//   );
// }
