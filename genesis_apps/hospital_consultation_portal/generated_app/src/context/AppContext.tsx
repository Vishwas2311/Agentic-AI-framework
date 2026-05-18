"use client";

import React, { createContext, useContext, useReducer, useEffect, ReactNode } from "react";
import { Consultation, Session, ConsultationStatus } from "@/types";

interface AppState {
  session: Session;
  consultations: Consultation[];
}

type Action =
  | { type: "LOGIN"; email: string }
  | { type: "LOGOUT" }
  | { type: "ADD_CONSULTATION"; consultation: Consultation }
  | { type: "UPDATE_STATUS"; id: string; status: ConsultationStatus }
  | { type: "HYDRATE"; state: AppState };

const initialState: AppState = {
  session: { isLoggedIn: false, patientEmail: "" },
  consultations: [],
};

const STORAGE_KEY = "hosp_portal_state";

function appReducer(state: AppState, action: Action): AppState {
  switch (action.type) {
    case "HYDRATE":
      return action.state;
    case "LOGIN":
      return { ...state, session: { isLoggedIn: true, patientEmail: action.email } };
    case "LOGOUT":
      return { ...state, session: { isLoggedIn: false, patientEmail: "" }, consultations: [] };
    case "ADD_CONSULTATION":
      return { ...state, consultations: [action.consultation, ...state.consultations] };
    case "UPDATE_STATUS":
      return {
        ...state,
        consultations: state.consultations.map((c) =>
          c.id === action.id
            ? {
                ...c,
                consultation_status: action.status,
                prescription_status: action.status === "Completed" ? "Available" : c.prescription_status,
              }
            : c
        ),
      };
    default:
      return state;
  }
}

interface AppContextValue {
  state: AppState;
  dispatch: React.Dispatch<Action>;
}

const AppContext = createContext<AppContextValue | null>(null);

export function AppProvider({ children }: { children: ReactNode }) {
  const [state, dispatch] = useReducer(appReducer, initialState);

  // Hydrate from localStorage on mount
  useEffect(() => {
    try {
      const raw = localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const saved: AppState = JSON.parse(raw);
        if (saved?.session) dispatch({ type: "HYDRATE", state: saved });
      }
    } catch {
      // ignore parse errors
    }
  }, []);

  // Persist to localStorage on every state change
  useEffect(() => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
    } catch {
      // ignore storage errors
    }
  }, [state]);

  return <AppContext.Provider value={{ state, dispatch }}>{children}</AppContext.Provider>;
}

export function useApp() {
  const ctx = useContext(AppContext);
  if (!ctx) throw new Error("useApp must be used within AppProvider");
  return ctx;
}
