// import { useState } from 'react';
import { useState, useEffect } from 'react';
// import { useNavigate } from 'react-router-dom';
import HeaderMenu from '../components/header-menu/headerMegaMenu';
import FooterLinks from '../components/footer/FooterLinks';
import FeaturesCards from './features-cards/FeaturesCards';
import LeadGrid from './home-grid/LeadGrid';
import { useAuth } from '../contexts/useAuth';
import { NavbarMinimal } from '../components/navbar/NavbarMinimal';
import { HeroText } from './hero-section/HeroText';
import './Homepage.css';
import Chatbot from '../components/chatbot/Chatbot';

const apiUrl = import.meta.env.VITE_API_URL;

function Homepage() {
  const [state] = useAuth();
  const [total_monetary_balance, set_total_monetary_balance] = useState(0);
  // const navigate = useNavigate();

  // const handleClick = () => {
  //     navigate('/contact');
  // };

  // Check loading state to prevent rendering issue
  if (state.loading) {
    return null;
  } else if (!state.loading && state.isAuthenticated) {
    console.log('Auth state:', state);
    // I need to perform a fetch here to the backend to get the users linked accounts and display them in the dashboard
    fetch(`${apiUrl}/customuser/${state.user.id}/accounts/`, {
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
        console.log('Accounts linked to User:', data);
        set_total_monetary_balance(data.total_balance);
      })
      .catch((error) => {
        console.error(`Fetch error: ${error}`);
      });
  }

  /* Example
  state = 
{
    "user": {
        "id": 1,
        "username": "user0",
        "email": "user0@example.com",
        "is_staff": false,
        "is_superuser": false,
        "role": "user"
    },
    "isAuthenticated": true,
    "loading": false
}
  */

  return (
    <>
      <div className="homepage-wrapper">
        <HeaderMenu />
        <div className="homepage-container">
          {!state.isAuthenticated ? (
            <div className="homepage-main-content">
              <HeroText />
              <div>
                <FeaturesCards />
              </div>
            </div>
          ) : (
            <div className="flex flex-row w-full min-h-[500px]">
              <div className="flex-shrink-0">
                <NavbarMinimal />
              </div>
              <div className="flex flex-1 min-w-0 min-h-[500px] align-center justify-center">
                <LeadGrid total_monetary_balance={total_monetary_balance} />
              </div>
            </div>
          )}
        </div>
        <FooterLinks />
        {state.isAuthenticated && <Chatbot />}
      </div>
    </>
  );
}

export default Homepage;
