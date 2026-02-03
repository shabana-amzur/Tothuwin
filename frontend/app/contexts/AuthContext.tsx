'use client';

import { createContext, useContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  profile_picture?: string;
  is_active?: boolean;
  created_at?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  loginWithToken: (token: string, userData: { email: string; username: string }) => Promise<void>;
  register: (data: any) => Promise<void>;
  logout: () => void;
  token: string | null;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for token in localStorage on mount
    const storedToken = localStorage.getItem('token');
    if (storedToken) {
      setToken(storedToken);
      fetchUser(storedToken);
    } else {
      setIsLoading(false);
    }
  }, []);

  const fetchUser = async (token: string) => {
    try {
      const response = await fetch('http://localhost:8001/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        logout();
      }
    } catch (error) {
      console.error('Failed to fetch user', error);
      logout();
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (username: string, password: string) => {
    // Note: The backend likely expects form-data for OAuth2 password flow, 
    // or JSON depending on implementation. 
    // Checking backend/app/main.py or api/auth.py is important.
    // Usually FastAPI OAuth2PasswordRequestForm expects form data 'username' and 'password'.
    // But api/auth.py had a custom UserLogin model? Let's check api/auth.py again.
    // Wait, I saw api/auth.py uses UserLogin pydantic model for a clear endpoint?
    // Let me double check api/auth.py content before assuming mechanism.
    
    // Assuming JSON based on previous read of api/auth.py (UserLogin schema).
    
    const response = await fetch('http://localhost:8001/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email: username, password }), // api/auth.py UserLogin has email, password
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    // Assuming response is { access_token: "...", token_type: "bearer" } or similar
    // Check api/auth.py return type.
    
    const newToken = data.access_token;
    localStorage.setItem('token', newToken);
    setToken(newToken);
    // Since login returns the user object inside the Token response, we can set it directly
    if (data.user) {
        setUser(data.user);
    } else {
        await fetchUser(newToken);
    }
    router.push('/');
  };

  const register = async (data: any) => {
    const response = await fetch('http://localhost:8001/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });

    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Registration failed');
    }
    
    const responseData = await response.json();
    const newToken = responseData.access_token;
    if (newToken) {
        localStorage.setItem('token', newToken);
        setToken(newToken);
        if (responseData.user) {
             setUser(responseData.user);
        } else {
             await fetchUser(newToken);
        }
        router.push('/');
    } else {
        router.push('/login');
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
    router.push('/login');
  };

  const loginWithToken = useCallback(async (newToken: string, userData: { email: string; username: string }) => {
    localStorage.setItem('token', newToken);
    setToken(newToken);
    // Try to fetch the full user data from the backend
    try {
      const response = await fetch('http://localhost:8001/api/auth/me', {
        headers: {
          Authorization: `Bearer ${newToken}`,
        },
      });

      if (response.ok) {
        const fullUserData = await response.json();
        setUser(fullUserData);
      } else {
        // Fallback: use data from URL if backend fetch fails
        console.warn('Failed to fetch user from backend, using OAuth data');
        setUser({ ...userData, id: 0, full_name: userData.username, role: 'user' } as User);
      }
    } catch (error) {
      console.error('Failed to fetch user after OAuth login:', error);
      // Fallback to setting user from URL data
      setUser({ ...userData, id: 0, full_name: userData.username, role: 'user' } as User);
    }
  }, []);

  const refreshUser = useCallback(async () => {
    if (!token) return;
    
    try {
      const response = await fetch('http://localhost:8001/api/auth/me', {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to refresh user data:', error);
    }
  }, [token]);

  return (
    <AuthContext.Provider value={{ user, isLoading, login, loginWithToken, register, logout, token, refreshUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
