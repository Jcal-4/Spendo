import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
// import ReactDOM from 'react-dom/client';
// import App from './App.tsx';
import Homepage from './Homepage/Homepage.tsx';
import ContactPage from './contact-page/ContactPage.tsx';
import '@mantine/core/styles.css';
import { MantineProvider } from '@mantine/core';

createRoot(document.getElementById('root')!).render(
    <StrictMode>
        <MantineProvider>
            <BrowserRouter>
                <Routes>
                    <Route path="" element={<Homepage />} />
                </Routes>
                <Routes>
                    <Route path="/contact" element={<ContactPage />} />
                </Routes>
            </BrowserRouter>
        </MantineProvider>
    </StrictMode>
);
