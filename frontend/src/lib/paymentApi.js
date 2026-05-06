import api from "@/lib/api";

export const createOrder = async (credits) => {
  const res = await api.post("/payments/create-order", { credits });
  return res.data;
};

export const verifyPayment = async (payload) => {
  const res = await api.post("/payments/verify", payload);
  return res.data;
};