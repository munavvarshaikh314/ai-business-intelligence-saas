import api from "@/lib/api";

export const fetchPaymentHistory = async () => {
  const res = await api.get("/payments/history");
  return res.data;
};

export const downloadInvoice = async (paymentId) => {
  const res = await api.get(`/invoices/download/${paymentId}`, {
    responseType: "blob",
  });

  return res.data;
};