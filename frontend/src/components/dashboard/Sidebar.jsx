"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

export default function Sidebar() {
  const pathname = usePathname();

  const menu = [
  { name: "Dashboard", path: "/dashboard" },
  { name: "Upload", path: "/dashboard/upload" },
  { name: "Analytics", path: "/dashboard/analytics" },
  { name: "Chatbot", path: "/dashboard/chatbot" },
  { name: "Billing", path: "/dashboard/billing" },
  { name: "Payments", path: "/dashboard/payments" },
  { name: "Settings", path: "/dashboard/settings" },
  { name: "Admin", path: "/dashboard/admin" }, // ✅ add this
];

  return (
    <div className="w-64 bg-white border-r shadow-sm p-4">
      <h1 className="text-xl font-bold mb-6">AI BI Dashboard</h1>

      <ul className="space-y-2">
        {menu.map((item) => (
          <li key={item.path}>
            <Link
              href={item.path}
              className={`block px-3 py-2 rounded text-sm ${
                pathname === item.path
                  ? "bg-black text-white"
                  : "hover:bg-gray-100"
              }`}
            >
              {item.name}
            </Link>
          </li>
        ))}
      </ul>
    </div>
  );
}