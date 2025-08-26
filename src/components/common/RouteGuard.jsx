import { useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';

const RouteGuard = ({ children }) => {
  const { isAuthenticated, logout } = useAuth();
  const location = useLocation();
  
  useEffect(() => {
    const landingPages = ['/', '/about', '/services', '/contact', '/quote', '/gallery', '/ndis', '/faq'];
    const isLandingPage = landingPages.includes(location.pathname);
    
    if (isAuthenticated && isLandingPage) {
      logout(true); 
    }
  }, [location.pathname, isAuthenticated, logout]);
  
  return children;
};

export default RouteGuard;
