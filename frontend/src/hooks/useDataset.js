"use client";
import { useContext } from "react";
import { DatasetContext } from "@/context/DatasetContext";

export function useDataset() {
  const ctx = useContext(DatasetContext);
  if (!ctx) throw new Error("useDataset must be used inside DatasetProvider");
  return ctx;
}
