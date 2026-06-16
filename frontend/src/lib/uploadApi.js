import api from "@/lib/api";

export const uploadCSV = async (datasetId, file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await api.post(`/upload/csv/${datasetId}`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percent);
      }
    },
  });

  return res.data;
};

export const uploadPDF = async (datasetId, file, onProgress) => {
  const formData = new FormData();
  formData.append("file", file);

  const res = await api.post(`/upload/pdf/${datasetId}`, formData, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
    timeout: 120000,
    onUploadProgress: (progressEvent) => {
      if (onProgress) {
        const percent = Math.round(
          (progressEvent.loaded * 100) / progressEvent.total
        );
        onProgress(percent);
      }
    },
  });

  return res.data;
};

export const fetchUploadStatus = async (datasetId) => {
  const res = await api.get(`/upload/status/${datasetId}`);
  return res.data;
};
