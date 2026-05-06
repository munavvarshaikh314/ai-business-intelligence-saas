import api from "@/lib/api";

export const fetchCredits = async () => {
  const res = await api.get("/credits/me");
  return res.data;
};