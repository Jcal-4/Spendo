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
import MyChat from '../components/chatbot/MyChat';

const apiUrl = import.meta.env.VITE_API_URL;

function Homepage() {
  const [state] = useAuth();
  const [user_balance, set_user_balance] = useState({
    cash_balance: 0,
    savings_balance: 0,
    investing_retirement: 0,
    total_balance: 0,
  });
  // const navigate = useNavigate();

  // const handleClick = () => {
  //     navigate('/contact');
  // };

  useEffect(() => {
    if (state.isAuthenticated && state.user?.id) {
      fetch(`${apiUrl}/customuser/${state.user.id}/accounts/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      })
        .then((response) => {
          if (!response.ok) {
            throw new Error(`HTTP Error! Status: ${response.status}`);
          }
          return response.json();
        })
        .then((data) => {
          console.log('user_balance', data);
          set_user_balance(data);
        })
        .catch((error) => {
          console.error(`Fetch error: ${error}`);
        });
    }
  }, [state.isAuthenticated, state.user?.id]);

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

  // Check loading state to prevent rendering issue
  if (state.loading) {
    return null;
  }
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
                <LeadGrid user_balance={user_balance} />
              </div>
              <MyChat user_balance={user_balance} />
            </div>
          )}
        </div>
        <FooterLinks />
        {/* {state.isAuthenticated && <Chatbot user_balance={user_balance} />} */}
      </div>
    </>
  );
}

export default Homepage;
