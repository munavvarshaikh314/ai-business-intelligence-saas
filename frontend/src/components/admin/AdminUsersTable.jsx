"use client";

import { useState } from "react";
import { updateUserCredits } from "@/lib/adminApi";

export default function AdminUsersTable({ users, onRefresh }) {
  const [editingId, setEditingId] = useState(null);
  const [newCredits, setNewCredits] = useState(0);

  const handleEdit = (user) => {
    setEditingId(user.id);
    setNewCredits(user.credits);
  };

  const handleSave = async (userId) => {
    try {
      await updateUserCredits(userId, newCredits);
      setEditingId(null);
      onRefresh();
    } catch (err) {
      alert("Failed to update credits");
    }
  };

  return (
    <div className="bg-white rounded shadow overflow-x-auto">
      <table className="w-full text-sm">
        <thead className="bg-gray-100">
          <tr>
            <th className="p-3 text-left">User ID</th>
            <th className="p-3 text-left">Name</th>
            <th className="p-3 text-left">Email</th>
            <th className="p-3 text-left">Credits</th>
            <th className="p-3 text-left">Action</th>
          </tr>
        </thead>

        <tbody>
          {users.map((u) => (
            <tr key={u.id} className="border-t">
              <td className="p-3">{u.id}</td>
              <td className="p-3">{u.name}</td>
              <td className="p-3">{u.email}</td>

              <td className="p-3">
                {editingId === u.id ? (
                  <input
                    type="number"
                    value={newCredits}
                    onChange={(e) => setNewCredits(Number(e.target.value))}
                    className="border p-1 rounded w-24"
                  />
                ) : (
                  u.credits
                )}
              </td>

              <td className="p-3">
                {editingId === u.id ? (
                  <button
                    onClick={() => handleSave(u.id)}
                    className="bg-black text-white px-3 py-1 rounded text-xs"
                  >
                    Save
                  </button>
                ) : (
                  <button
                    onClick={() => handleEdit(u)}
                    className="text-blue-600 underline text-xs"
                  >
                    Edit Credits
                  </button>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}