import api from "@/lib/api";

export const createOrder = async (credits) => {
  const amount = Number(credits) * 100;
  const res = await api.post("/payments/create-order", { amount });
  const data = res.data;

  return {
    ...data,
    key: data.razorpay_key_id || data.key_id || process.env.NEXT_PUBLIC_RAZORPAY_KEY_ID,
    amount: data.amount || amount,
    credits: data.credits || Number(credits),
    currency: data.currency || "INR",
  };
};

export const verifyPayment = async (payload) => {
  const res = await api.post("/payments/verify", payload);
  return res.data;
};
