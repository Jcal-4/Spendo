import React, { useReducer, useEffect, ReactNode } from 'react';
import { fetchMe } from '../api/auth';
import type { User } from '../api/auth';
import { AuthContext } from './AuthContext';
import type { AuthState, AuthContextValue } from './AuthContext';

const apiUrl = import.meta.env.VITE_API_URL;

const initialState: AuthState = {
    user: null,
    isAuthenticated: false,
    loading: true,
};

function authReducer(state: AuthState, action: any): AuthState {
    switch (action.type) {
        case 'SET_USER':
            return { ...state, user: action.payload, isAuthenticated: true, loading: false };
        case 'CLEAR_USER':
            return { user: null, isAuthenticated: false, loading: false };
        case 'SET_LOADING':
            return { ...state, loading: action.payload };
        default:
            return state;
    }
}

export const AuthProvider = ({ children }: { children: ReactNode }) => {
    const [state, dispatch] = useReducer(authReducer, initialState);

    useEffect(() => {
        (async () => {
            try {
                const user = await fetchMe();
                dispatch({ type: 'SET_USER', payload: user });
            } catch {
                dispatch({ type: 'CLEAR_USER' });
            }
        })();
    }, []);

    // Utility to get cookie value
    function getCookie(name: string) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop()?.split(';').shift();
    }

    const login = async (credentials: { username: string; password: string }) => {
        // Fetch CSRF token first
        await fetch(`${apiUrl}/csrf/`, { credentials: 'include' });
        const csrftoken = getCookie('csrftoken');
        await fetch(`${apiUrl}/login/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrftoken || '',
            },
            credentials: 'include',
            body: JSON.stringify(credentials),
        });
        const user = await fetchMe();
        dispatch({ type: 'SET_USER', payload: user });
    };

    const logout = async () => {
        await fetch('/logout/', { method: 'POST', credentials: 'include' });
        dispatch({ type: 'CLEAR_USER' });
    };

    return <AuthContext.Provider value={[state, { login, logout }]}>{children}</AuthContext.Provider>;
};

// useAuth moved to useAuth.ts
