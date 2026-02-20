"use client";

import { createContext, useContext, useEffect, useState } from "react";

interface User {
    uid: string;
    email: string;
    token?: string;
}

interface AuthContextType {
    user: User | null;
    userData: any;
    loading: boolean;
    login: (userData: User, extraData?: any) => void;
    logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [userData, setUserData] = useState<any>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const storedUser = localStorage.getItem("oracle_user");
        const storedData = localStorage.getItem("oracle_user_data");
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
                if (storedData) setUserData(JSON.parse(storedData));
            } catch (e) {
                localStorage.removeItem("oracle_user");
                localStorage.removeItem("oracle_user_data");
            }
        }
        setLoading(false);
    }, []);

    const login = (userData: User, extraData: any = null) => {
        setUser(userData);
        setUserData(extraData);
        localStorage.setItem("oracle_user", JSON.stringify(userData));
        if (extraData) localStorage.setItem("oracle_user_data", JSON.stringify(extraData));
    };

    const logout = () => {
        setUser(null);
        setUserData(null);
        localStorage.removeItem("oracle_user");
        localStorage.removeItem("oracle_user_data");
    };

    return (
        <AuthContext.Provider value={{ user, userData, loading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return context;
}
