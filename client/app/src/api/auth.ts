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
