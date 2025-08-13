import React from 'react';
import { Navigate } from 'react-router-dom';
import { useAuth } from '../contexts/useAuth';

interface ProtectedRouteProps {
    children: JSX.Element;
    role?: string; // Optional (e.g. "admin")
    redirectTo?: string;
}

export function ProtectedRoute({ children, role, redirectTo = '/login' }: ProtectedRouteProps) {
    const [auth] = useAuth();
    const { isAuthenticated, loading, user } = auth;

    if (loading) return <div>Loading...</div>;
    if (!isAuthenticated) return <Navigate to={redirectTo} replace />;
    if (role && user?.role !== role) return <div>Access denied</div>;

    return children;
}
