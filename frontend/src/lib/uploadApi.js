import api from "@/lib/api";

const uploadFile = async (url, file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await api.post(url, formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (!event.total || !onProgress) return;
      onProgress(Math.round((event.loaded * 100) / event.total));
    },
  });

  return res.data;
};

export const uploadCSV = (datasetId, file, onProgress) =>
  uploadFile(`/upload/csv/${datasetId}`, file, onProgress);

export const uploadPDF = (datasetId, file, onProgress) =>
  uploadFile(`/upload/pdf/${datasetId}`, file, onProgress);
