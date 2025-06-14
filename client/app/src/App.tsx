// import { useState } from 'react';
// import reactLogo from './assets/react.svg';
// import viteLogo from '/vite.svg';
import './App.css';
import { useEffect } from 'react';
const apiUrl = import.meta.env.VITE_API_URL;

function App() {
    useEffect(() => {
        console.log(apiUrl);
        fetchData();
    }, []);

    const fetchData = () => {
        fetch(`${apiUrl}/customusers/`, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
            },
        })
            .then((response) => {
                console.log(response)
                if (!response.ok) {
                    throw new Error(`HTTP Error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then((data) => {
                // debugger;
                console.log(data);
            })
            .catch((error) => {
                console.error(`Fetch error: ${error}`);
            });
    };

    return (
        <>
            <div>Django-React (Database Implemented).</div>
        </>
    );
}

export default App;
