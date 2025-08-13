import { createContext } from 'react';
import type { User } from '../api/auth';

export interface AuthState {
    user: User | null;
    isAuthenticated: boolean;
    loading: boolean;
}

type AuthAction = { type: 'SET_USER'; payload: User } | { type: 'CLEAR_USER' } | { type: 'SET_LOADING'; payload: boolean };

export type AuthContextValue = [
    AuthState,
    {
        login: (credentials: { username: string; password: string }) => Promise<void>;
        logout: () => Promise<void>;
    },
];

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
