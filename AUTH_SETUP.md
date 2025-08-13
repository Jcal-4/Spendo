# Spendo Authentication Setup Guide

This guide documents all the steps, files, and configuration changes made to enable secure session authentication between the React frontend and Django backend.

---

## Frontend (React)

### 1. Context and Hook Files (Full Code Examples)

#### `client/app/src/contexts/AuthContext.ts`

```typescript
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
```

#### `client/app/src/contexts/AuthContext.tsx`

```tsx
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
```

#### `client/app/src/contexts/useAuth.ts`

```typescript
import { useContext } from 'react';
import { AuthContext } from './AuthContext';

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) throw new Error('useAuth must be used within AuthProvider');
    return ctx;
}
```

#### `client/app/src/api/auth.ts`

```typescript
const apiUrl = import.meta.env.VITE_API_URL;
export type User = {
    id: number;
    username: string;
    email: string;
    role: string;
};

export const fetchMe = async (): Promise<User> => {
    const res = await fetch(`${apiUrl}/me/`, { credentials: 'include' });
    if (!res.ok) throw new Error('Unauthenticated');
    return res.json();
};
```

#### `client/app/src/authentication-page/AuthenticationPage.tsx` (Minimal Auth Example)

```tsx
import { useState } from 'react';
import { useAuth } from '../contexts/useAuth';

export function AuthenticationPage() {
    const [form, setForm] = useState({ username: '', password: '' });
    const [state, { login }] = useAuth();

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
        setForm((f) => ({ ...f, [e.target.name]: e.target.value }));
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        await login(form);
    };

    return (
        <div>
            {state.isAuthenticated && state.user ? (
                <div>Logged in as <b>{state.user.username}</b></div>
            ) : (
                <form onSubmit={handleSubmit}>
                    <input
                        name="username"
                        onChange={handleChange}
                        placeholder="Username"
                    />
                    <input
                        name="password"
                        type="password"
                        onChange={handleChange}
                        placeholder="Password"
                    />
                    <button type="submit">Login</button>
                </form>
            )}
        </div>
    );
}
```

#### Logout Functionality (Minimal Example)

The `logout` function is provided by the AuthProvider and can be accessed via the `useAuth` hook. It sends a POST request to the backend logout endpoint and clears the user state on the frontend.

**Minimal usage example:**

```tsx
import { useAuth } from '../contexts/useAuth';

export function LogoutButton() {
    const [, { logout }] = useAuth();

    return <button onClick={logout}>Logout</button>;
}
```

You can place this button anywhere in your app where you want to allow the user to log out. When clicked, it will log the user out on the backend and update the UI accordingly.

### 2. Usage

- Wrap your app in `<AuthProvider>` in `main.tsx` or `App.tsx`:
    ```tsx
    <AuthProvider>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </AuthProvider>
    ```
- Use `useAuth()` in any component to access authentication state and actions.

### 3. CSRF Handling

- Before login, the frontend fetches `/api/csrf/` to set the CSRF cookie.
- The CSRF token is read from the cookie and sent in the `X-CSRFToken` header with the login request.

### 4. API URL Consistency and Trailing Slashes

- **Always use the `VITE_API_URL` environment variable for all API calls in the frontend.**
    - Example in `.env`:
        ```env
        VITE_API_URL=http://localhost:8000/api
        ```
- **Ensure all API calls match the backend route, including trailing slashes.**
    - For example, if your backend route is `/api/me/`, your frontend should call `${apiUrl}/me/` (not `${apiUrl}/me`).
    - This prevents issues with Django route matching and ensures requests reach the correct endpoint.
    - Example fetch:
        ```typescript
        export const fetchMe = async (): Promise<User> => {
            const res = await fetch(`${apiUrl}/me/`, { credentials: 'include' });
            if (!res.ok) throw new Error('Unauthenticated');
            return res.json();
        };
        ```

---

## Backend (Django)

    ```python
    'corsheaders',

- Add to `MIDDLEWARE` (at the top):

### 1. Context and Hook Files

- **Created `client/app/src/contexts/AuthContext.ts`**

    - **Exports:**
        - `export const AuthContext = createContext<AuthContextValue | undefined>(undefined);`
        - `export interface AuthState { ... }`
        - `export type AuthContextValue = [...]`

- **Created `client/app/src/contexts/AuthContext.tsx`**

    - **Imports:**
        - `import { AuthContext } from './AuthContext';`
        - `import type { AuthState, AuthContextValue } from './AuthContext';`
        - `import { fetchMe } from '../api/auth';`
        - `import type { User } from '../api/auth';`
    - **Exports:**
        - `export const AuthProvider = ({ children }: { children: ReactNode }) => { ... }`
    - Provides the `AuthProvider` component, which manages authentication state and exposes `login` and `logout` functions.
    - Handles CSRF token fetching before login and includes it in the login request.

- **Created `client/app/src/contexts/useAuth.ts`**
    - **Imports:**
        - `import { useContext } from 'react';`
        - `import { AuthContext } from './AuthContext';`
    - **Exports:**
        - `export function useAuth() { ... }`
    - Exports the `useAuth` hook for accessing authentication state and actions.
    ```python
    'corsheaders.middleware.CorsMiddleware',
    ```
- Add CORS and CSRF settings:
    ```python
    CORS_ALLOW_CREDENTIALS = True
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:5173",
        "http://localhost:3000",
        "http://spendo-386e7e9da44d.herokuapp.com"
    ```

### 2. Usage

- **Wrap your app in `<AuthProvider>` in `main.tsx` or `App.tsx`:**
    ```tsx
    import { AuthProvider } from './contexts/AuthContext.tsx';
    // ...
    <AuthProvider>
        <BrowserRouter>
            <App />
        </BrowserRouter>
    </AuthProvider>;
    ```
- **Use `useAuth()` in any component to access authentication state and actions:**
    ```tsx
    import { useAuth } from '../contexts/useAuth';
    const [, { login, logout }] = useAuth();
    ```
    CSRF_TRUSTED_ORIGINS = [
    "http://localhost:5173",

### 3. CSRF Handling

- Before login, the frontend fetches `/api/csrf/` to set the CSRF cookie.
- The CSRF token is read from the cookie and sent in the `X-CSRFToken` header with the login request.
  ]
  AUTHENTICATION_BACKENDS = [
  ]

    ```

    ```

### 2. CSRF Endpoint

- Add a view to provide the CSRF cookie:

    ```python
    from django.views.decorators.csrf import ensure_csrf_cookie
    from django.http import JsonResponse
    @ensure_csrf_cookie
    def get_csrf(request):
        return JsonResponse({'detail': 'CSRF cookie set'})
    ```

### 2. CSRF Endpoint

- **Add a view to provide the CSRF cookie:**

    ```python
    from django.views.decorators.csrf import ensure_csrf_cookie
    from django.http import JsonResponse

    @ensure_csrf_cookie
    def get_csrf(request):
            return JsonResponse({'detail': 'CSRF cookie set'})
    ```

- **Add to `urls.py`:**

    ```python
    from .views import get_csrf
    path('api/csrf/', get_csrf),
    ```

    ````

    ```python
    path('api/csrf/', get_csrf),
    ````

### 3. Custom Login API Endpoint

- In `api/views.py`, add:

    ```python
    from django.contrib.auth import authenticate, login
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework import status

    class LoginView(APIView):
        def post(self, request):
            username = request.data.get('username')
            password = request.data.get('password')
            if user is not None:
                login(request, user)
                return Response({'detail': 'Logged in'})
    ```

### 3. Custom Login API Endpoint

- **In `api/views.py`, add:**

    ```python
    from django.contrib.auth import authenticate, login
    from rest_framework.views import APIView
    from rest_framework.response import Response
    from rest_framework import status

    class LoginView(APIView):
            def post(self, request):
                    username = request.data.get('username')
                    password = request.data.get('password')
                    user = authenticate(request, username=username, password=password)
                    if user is not None:
                            login(request, user)
                            return Response({'detail': 'Logged in'})
                    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)
    ```

- **Add to `urls.py`:**

    ```python
    from .views import LoginView
    path('api/login/', LoginView.as_view(), name='api-login'),
    ```

                    return Response({'detail': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)

    ```

    ```

- Add to `urls.py`:
    ```python
    path('api/login/', LoginView.as_view(), name='api-login'),
    ```

### 4. User Creation (for testing)

- When creating users in scripts, always use `set_password`:
    ```python
    user.set_password('password')
    user.save()
    ```

---

## Summary

- The frontend uses a context/provider/hook pattern for authentication and handles CSRF tokens.
- The backend is configured for CORS and CSRF, provides a CSRF endpoint, and exposes a custom login API.
- User creation scripts must use `set_password` for authentication to work.

This setup enables secure, session-based authentication between your React frontend and Django backend.
`````
