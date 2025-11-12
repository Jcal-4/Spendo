import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext.tsx';
// import ReactDOM from 'react-dom/client';
// import App from './App.tsx';
import HomePage from './pages/HomePage/HomePage.tsx';
import AuthenticationPage from './pages/AuthenticationPage/AuthenticationPage';
import './index.css';
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';
import { Provider } from '@/components/ui/provider';

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Provider>
      <MantineProvider>
        <AuthProvider>
          <BrowserRouter>
            <Routes>
              <Route path="/" element={<HomePage />} />
            </Routes>
            <Routes>
              <Route path="/login" element={<AuthenticationPage />} />
            </Routes>
          </BrowserRouter>
        </AuthProvider>
      </MantineProvider>
    </Provider>
  </StrictMode>
);
