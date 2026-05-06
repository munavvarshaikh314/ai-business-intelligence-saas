"use client";

import { useCredits } from "@/context/CreditsContext";

export default function CreditsBadge() {
  const { credits, loadingCredits } = useCredits();

  if (loadingCredits) return <p className="text-sm">Credits: ...</p>;

  return (
    <div className="px-3 py-2 bg-white border rounded shadow text-sm">
      Credits: <span className="font-bold">{credits}</span>
    </div>
  );
}