"use client";

import { createContext, useContext, useEffect, useState } from "react";
import { fetchCredits } from "@/lib/creditsApi";

const CreditsContext = createContext();

export function CreditsProvider({ children }) {
  const [credits, setCredits] = useState(0);
  const [loadingCredits, setLoadingCredits] = useState(true);

  const loadCredits = async () => {
    setLoadingCredits(true);
    try {
      const data = await fetchCredits();
      setCredits(data.credits);
    } catch (err) {
      setCredits(0);
    } finally {
      setLoadingCredits(false);
    }
  };

const { user } = useAuth();

useEffect(() => {
  if (user) {
    loadCredits();
  } else {
    setCredits(0);
  }
}, [user]);

  return (
    <CreditsContext.Provider
      value={{
        credits,
        setCredits,
        loadCredits,
        loadingCredits,
      }}
    >
      {children}
    </CreditsContext.Provider>
  );
}

export function useCredits() {
  return useContext(CreditsContext);
}