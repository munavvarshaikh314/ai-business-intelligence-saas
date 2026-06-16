"use client";

import { useState } from "react";
import { changePassword } from "@/lib/settingsApi";
import { getErrorMessage } from "@/lib/errors";

export default function PasswordForm() {
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState("");
  const [error, setError] = useState("");

  const handleChange = async (e) => {
    e.preventDefault();
    setSuccess("");
    setError("");

    if (!oldPassword) { setError("Please enter your current password."); return; }
    if (!newPassword) { setError("Please enter a new password."); return; }
    if (newPassword.length < 6) { setError("New password must be at least 6 characters."); return; }
    if (oldPassword === newPassword) { setError("New password must be different from your current password."); return; }

    setLoading(true);
    try {
      await changePassword({ old_password: oldPassword, new_password: newPassword });
      setSuccess("Password updated successfully.");
      setOldPassword("");
      setNewPassword("");
    } catch (err) {
      setError(getErrorMessage(err, "Failed to update password. Please check your current password and try again."));
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleChange} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
      <h2 className="mb-4 text-lg font-bold text-slate-950">Change Password</h2>

      {error && (
        <div className="mb-3 rounded-md border border-red-200 bg-red-50 px-3 py-2 text-sm text-red-700">{error}</div>
      )}
      {success && (
        <div className="mb-3 rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm text-emerald-700">✓ {success}</div>
      )}

      <label className="mb-1 block text-sm font-medium text-slate-700">Current Password</label>
      <input
        className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        type="password"
        value={oldPassword}
        onChange={(e) => { setError(""); setOldPassword(e.target.value); }}
      />

      <label className="mb-1 block text-sm font-medium text-slate-700">New Password</label>
      <input
        className="mb-4 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
        type="password"
        placeholder="Min 6 characters"
        value={newPassword}
        onChange={(e) => { setError(""); setNewPassword(e.target.value); }}
      />

      <button
        disabled={loading}
        className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300 disabled:cursor-not-allowed"
      >
        {loading ? "Updating..." : "Update Password"}
      </button>
    </form>
  );
}




// "use client";

// import { useState } from "react";
// import { changePassword } from "@/lib/settingsApi";

// export default function PasswordForm() {
//   const [oldPassword, setOldPassword] = useState("");
//   const [newPassword, setNewPassword] = useState("");

//   const [loading, setLoading] = useState(false);
//   const [msg, setMsg] = useState("");

//   const handleChange = async (e) => {
//     e.preventDefault();
//     setLoading(true);
//     setMsg("");

//     try {
//       await changePassword({ old_password: oldPassword, new_password: newPassword });
//       setMsg("Password updated successfully.");
//       setOldPassword("");
//       setNewPassword("");
//     } catch (err) {
//       setMsg("Failed to update password.");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <form onSubmit={handleChange} className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
//       <h2 className="mb-4 text-lg font-bold text-slate-950">Change Password</h2>

//       <label className="mb-1 block text-sm font-medium text-slate-700">Old Password</label>
//       <input
//         className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
//         type="password"
//         value={oldPassword}
//         onChange={(e) => setOldPassword(e.target.value)}
//       />

//       <label className="mb-1 block text-sm font-medium text-slate-700">New Password</label>
//       <input
//         className="mb-3 w-full rounded-md border border-slate-200 p-2 outline-none focus:border-emerald-400"
//         type="password"
//         value={newPassword}
//         onChange={(e) => setNewPassword(e.target.value)}
//       />

//       <button
//         disabled={loading}
//         className="rounded-md bg-slate-950 px-4 py-2 text-sm font-semibold text-white transition hover:bg-emerald-700 disabled:bg-slate-300"
//       >
//         {loading ? "Updating..." : "Update Password"}
//       </button>

//       {msg && <p className="mt-3 text-sm text-emerald-700">{msg}</p>}
//     </form>
//   );
// }
