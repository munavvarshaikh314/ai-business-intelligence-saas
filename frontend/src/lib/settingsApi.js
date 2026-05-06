import api from "@/lib/api";

export const updateProfile = async (payload) => {
  const res = await api.put("/auth/update-profile", payload);
  return res.data;
};

export const updatePreferences = async (payload) => {
  const res = await api.put("/auth/update-preferences", payload);
  return res.data;
};

export const changePassword = async (payload) => {
  const res = await api.put("/auth/change-password", payload);
  return res.data;
};