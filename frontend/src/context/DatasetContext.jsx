"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { fetchDatasets, createDataset, deleteDataset } from "@/lib/datasetApi";
import { DatasetErrors } from "@/lib/errors";

const DatasetContext = createContext();

export function DatasetProvider({ children }) {
  const [datasets, setDatasets] = useState([]);
  const [activeDataset, setActiveDataset] = useState(null);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState("");

  const loadDatasets = async () => {
    setLoading(true);
    setLoadError("");
    try {
      const data = await fetchDatasets();
      setDatasets(data);

      const savedId = localStorage.getItem("activeDatasetId");
      if (savedId) {
        const found = data.find((d) => d.id === savedId);
        if (found) setActiveDataset(found);
        else if (data.length > 0) {
          setActiveDataset(data[0]);
          localStorage.setItem("activeDatasetId", data[0].id);
        }
      } else if (data.length > 0) {
        setActiveDataset(data[0]);
        localStorage.setItem("activeDatasetId", data[0].id);
      }
    } catch (err) {
      setLoadError(DatasetErrors.load(err));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDatasets();
  }, []);

  const selectDataset = (dataset) => {
    setActiveDataset(dataset);
    localStorage.setItem("activeDatasetId", dataset.id);
  };

  const addDataset = async (name, description, datasetType = "CSV") => {
    const newDataset = await createDataset(name, description, datasetType);
    await loadDatasets();
    selectDataset(newDataset);
    return newDataset;
  };

  const removeDataset = async (datasetId) => {
    await deleteDataset(datasetId);
    if (activeDataset?.id === datasetId) {
      setActiveDataset(null);
      localStorage.removeItem("activeDatasetId");
    }
    await loadDatasets();
  };

  return (
    <DatasetContext.Provider
      value={{
        datasets,
        activeDataset,
        loading,
        loadError,
        loadDatasets,
        selectDataset,
        addDataset,
        removeDataset,
      }}
    >
      {children}
    </DatasetContext.Provider>
  );
}

export function useDataset() {
  return useContext(DatasetContext);
}





// "use client";

// import { createContext, useContext, useEffect, useState } from "react";
// import { fetchDatasets, createDataset, deleteDataset } from "@/lib/datasetApi";

// const DatasetContext = createContext();

// export function DatasetProvider({ children }) {
//   const [datasets, setDatasets] = useState([]);
//   const [activeDataset, setActiveDataset] = useState(null);
//   const [loading, setLoading] = useState(true);

//   const loadDatasets = async () => {
//     setLoading(true);
//     try {
//       const data = await fetchDatasets();
//       setDatasets(data);

//       const savedId = localStorage.getItem("activeDatasetId");

//       if (savedId) {
//         const found = data.find((d) => d.id === savedId);
//         if (found) setActiveDataset(found);
//       } else if (data.length > 0) {
//         setActiveDataset(data[0]);
//         localStorage.setItem("activeDatasetId", data[0].id);
//       }
//     } catch (err) {
//       console.log("Failed to load datasets");
//     } finally {
//       setLoading(false);
//     }
//   };

//   useEffect(() => {
//     loadDatasets();
//   }, []);

//   const selectDataset = (dataset) => {
//     setActiveDataset(dataset);
//     localStorage.setItem("activeDatasetId", dataset.id);
//   };

//   const addDataset = async (name, description, datasetType = "CSV") => {
//     const newDataset = await createDataset(name, description, datasetType);
//     await loadDatasets();
//     selectDataset(newDataset);
//     return newDataset;
//   };

//   const removeDataset = async (datasetId) => {
//     await deleteDataset(datasetId);
//     await loadDatasets();
//   };

//   return (
//     <DatasetContext.Provider
//       value={{
//         datasets,
//         activeDataset,
//         loading,
//         loadDatasets,
//         selectDataset,
//         addDataset,
//         removeDataset,
//       }}
//     >
//       {children}
//     </DatasetContext.Provider>
//   );
// }

// export function useDataset() {
//   return useContext(DatasetContext);
// }
