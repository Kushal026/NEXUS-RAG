"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { UserAccount } from "../types";
import { api } from "../services/api";

interface AuthContextType {
  user: UserAccount | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (usernameOrEmail: string, password: string) => Promise<void>;
  register: (username: string, email: string, password: string, name?: string) => Promise<void>;
  continueWithGoogle: () => Promise<void>;
  forgotPassword: (email: string) => Promise<{ status: string; message: string; reset_token?: string }>;
  resetPassword: (token: string, newPassword: string) => Promise<{ status: string; message: string }>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<UserAccount | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Restore session on mount
  useEffect(() => {
    const restoreSession = async () => {
      const storedToken = api.getAuthToken();
      if (storedToken) {
        setToken(storedToken);
        try {
          const profile = await api.getMe();
          setUser(profile);
        } catch (err) {
          console.warn("Session restore failed, clearing token:", err);
          api.setAuthToken(null);
          setToken(null);
          setUser(null);
        }
      }
      setIsLoading(false);
    };

    restoreSession();
  }, []);

  const login = async (usernameOrEmail: string, password: string) => {
    setIsLoading(true);
    try {
      const res = await api.login(usernameOrEmail, password);
      setToken(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (username: string, email: string, password: string, name?: string) => {
    setIsLoading(true);
    try {
      const res = await api.register(username, email, password, name);
      setToken(res.access_token);
      setUser(res.user);
    } finally {
      setIsLoading(false);
    }
  };

  const continueWithGoogle = async () => {
    setIsLoading(true);
    try {
      // Simulate OAuth or log into Google researcher profile
      const googleUsername = `google_researcher_${Math.floor(1000 + Math.random() * 9000)}`;
      const googleEmail = `${googleUsername}@gmail.com`;
      try {
        const res = await api.register(googleUsername, googleEmail, "GoogleAuthSecure2026!", "Google Researcher");
        setToken(res.access_token);
        setUser(res.user);
      } catch {
        const res = await api.login(googleUsername, "GoogleAuthSecure2026!");
        setToken(res.access_token);
        setUser(res.user);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const forgotPassword = async (email: string) => {
    return api.forgotPassword(email);
  };

  const resetPassword = async (token: string, newPassword: string) => {
    return api.resetPassword(token, newPassword);
  };

  const logout = async () => {
    setIsLoading(true);
    try {
      await api.logout();
    } finally {
      setToken(null);
      setUser(null);
      setIsLoading(false);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!user && !!token,
        isLoading,
        login,
        register,
        continueWithGoogle,
        forgotPassword,
        resetPassword,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = (): AuthContextType => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
