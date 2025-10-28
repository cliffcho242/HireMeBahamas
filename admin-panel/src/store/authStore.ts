import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface Admin {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
}

interface AuthStore {
  admin: Admin | null;
  token: string | null;
  isAuthenticated: boolean;
  setAuth: (admin: Admin, token: string) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthStore>()(
  persist(
    (set) => ({
      admin: null,
      token: null,
      isAuthenticated: false,
      setAuth: (admin, token) => {
        localStorage.setItem('admin_token', token);
        set({ admin, token, isAuthenticated: true });
      },
      logout: () => {
        localStorage.removeItem('admin_token');
        set({ admin: null, token: null, isAuthenticated: false });
      },
    }),
    {
      name: 'admin-auth-storage',
    }
  )
);
