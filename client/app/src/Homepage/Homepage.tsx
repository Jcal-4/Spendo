// import { useState } from 'react';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
// import "./index.css"

const apiUrl = import.meta.env.VITE_API_URL;

function Homepage() {
    const navigate = useNavigate();

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
                console.log(response);
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
            <p>Testing</p>
        </>
    );
}

export default Homepage;
