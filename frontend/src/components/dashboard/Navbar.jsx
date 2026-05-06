"use client";

import DatasetSelector from "./DatasetSelector";
import CreditsBadge from "./CreditsBadge";
import Link from "next/link";
import { useAuth } from "@/context/AuthContext";

export default function Navbar() {
  const { user } = useAuth();

  return (
    <div className="w-full bg-white border-b shadow-sm p-4 flex justify-between items-center">
      <div className="flex items-center gap-4">
        <DatasetSelector />
      </div>

      <div className="flex items-center gap-4">
        <CreditsBadge />

        <Link
          href="/dashboard/settings"
          className="text-sm font-semibold text-gray-700 hover:underline"
        >
          {user?.name || "Account"}
        </Link>
      </div>
    </div>
  );
}