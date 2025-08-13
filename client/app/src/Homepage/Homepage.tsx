// import { useState } from 'react';
import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import HeaderMenu from '../components/header-menu/headerMegaMenu';
import Footer from '../components/footer/Footer';
import FeaturesCards from './features-cards/FeaturesCards'
import { useAuth } from '../contexts/useAuth'
// import "./index.css"

const apiUrl = import.meta.env.VITE_API_URL;

function Homepage() {
    const [state] = useAuth();
    const navigate = useNavigate();

    const handleClick = () => {
        navigate('/contact');
    };

    useEffect(() => {
        console.log(apiUrl);
        fetchData();
    }, []);

    const fetchData = (): void => {
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
            <HeaderMenu/>
            <FeaturesCards/>
            <Footer />
        </>
    );
}

export default Homepage;
