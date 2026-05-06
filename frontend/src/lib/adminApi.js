import api from "@/lib/api";

export const fetchAllUsers = async () => {
  const res = await api.get("/admin/users");
  return res.data;
};

export const updateUserCredits = async (userId, credits) => {
  const res = await api.put(`/admin/users/${userId}/credits`, { credits });
  return res.data;
};

export const fetchAllPayments = async () => {
  const res = await api.get("/admin/payments");
  return res.data;
};

export const fetchUsageLogs = async () => {
  const res = await api.get("/admin/usage-logs");
  return res.data;
};