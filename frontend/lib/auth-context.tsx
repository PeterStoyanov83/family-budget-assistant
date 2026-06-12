"use client";

import { createContext, useContext, useEffect, useState, ReactNode } from "react";
import { authApi, User } from "@/lib/api";

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  setUser: (user: User | null) => void;
}

const AuthContext = createContext<AuthContextValue>({
  user: null,
  loading: true,
  setUser: () => {},
});

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authApi
      .me()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
