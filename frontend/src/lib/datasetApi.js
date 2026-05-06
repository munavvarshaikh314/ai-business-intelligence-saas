import api from "@/lib/api";

export const fetchDatasets = async () => {
  const res = await api.get("/datasets/");
  return res.data;
};

export const createDataset = async (datasetName, description = "", datasetType = "CSV") => {
  const res = await api.post("/datasets/create", {
    dataset_name: datasetName,
    dataset_type: datasetType,
    description,
  });
  return res.data;
};

export const deleteDataset = async (datasetId) => {
  const res = await api.delete(`/datasets/${datasetId}`);
  return res.data;
};
