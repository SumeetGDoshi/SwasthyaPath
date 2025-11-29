"use client";

import React, { createContext, useContext, useState, useEffect, ReactNode } from "react";
import { User } from "@/lib/api";

// Default demo user - no login required
const DEMO_USER: User = {
    id: "demo-user-123",
    email: "demo@swasthyapath.com",
    name: "Rahul Kumar",
    phone: "+91 98765 43210",
};

interface AuthContextType {
    user: User;
    isAuthenticated: boolean;
    isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
    children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // Simulate brief loading then set ready
        setIsLoading(false);
    }, []);

    const value: AuthContextType = {
        user: DEMO_USER,
        isAuthenticated: true,
        isLoading,
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
