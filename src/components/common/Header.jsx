import { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../common/Button.jsx';
import ThemeToggle from './ThemeToggle.jsx';
import { NAVIGATION_LINKS, COMPANY_INFO } from '../../utils/constants.js';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);
  const [activeDropdown, setActiveDropdown] = useState(null);
  const location = useLocation();
  const headerRef = useRef(null);
  const { isAuthenticated, user, logout } = useAuth();

  const landingPages = ['/', '/about', '/services', '/contact', '/quote', '/gallery', '/ndis', '/faq'];
  const isEmailVerificationPage = location.pathname.includes('/email-verification') || 
                               location.pathname.includes('/verify-email') ||
                               location.search.includes('token=');
  const isLandingPage = landingPages.includes(location.pathname);
  const showAuthButtons = isAuthenticated && !isLandingPage && !isEmailVerificationPage;

  useEffect(() => {
    const handleScroll = () => {
      setIsScrolled(window.scrollY > 20);
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  useEffect(() => {
    setIsMenuOpen(false);
    setActiveDropdown(null);
  }, [location]);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (headerRef.current && !headerRef.current.contains(event.target)) {
        setActiveDropdown(null);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const toggleDropdown = (dropdown) => {
    setActiveDropdown(activeDropdown === dropdown ? null : dropdown);
  };

  const handleLogout = async () => {
    if (window.quotesRefreshInterval) {
      clearInterval(window.quotesRefreshInterval);
      window.quotesRefreshInterval = null;
    }
    if (window.invoicesRefreshInterval) {
      clearInterval(window.invoicesRefreshInterval);
      window.invoicesRefreshInterval = null;
    }
    await logout();
  };

  const servicesDropdown = [
    { name: 'General Home Cleaning', path: '/services#general', icon: '🏠' },
    { name: 'Deep Cleaning', path: '/services#deep', icon: '✨' },
    { name: 'End-of-Lease Cleaning', path: '/services#end-of-lease', icon: '🔑' },
    { name: 'NDIS Cleaning Support', path: '/services#ndis', icon: '🛡️' },
    { name: 'office and commecial cleaning', path: '/services#pet-treatment', icon: '🐕' },
    { name: 'Window & Carpet Cleaning', path: '/services#window-carpet', icon: '🪟' }
  ];

  const resourcesDropdown = [
    { name: 'FAQ', path: '/faq', icon: '❓' },
    { name: 'Gallery', path: '/gallery', icon: '📸' },
    { name: 'NDIS Information', path: '/ndis', icon: '📋' },
    { name: 'Cleaning Tips', path: '/blog', icon: '💡' }
  ];

  const isActivePath = (path) => {
    if (path === '/') return location.pathname === '/';
    return location.pathname.startsWith(path);
  };

  return (
    <header ref={headerRef} className="fixed top-2 left-2 right-2 z-[100] transition-all duration-700 ease-out">
      <div className="absolute inset-0 -z-10">
        <div className="absolute top-0 left-1/4 w-32 h-32 bg-[#006da6]/20 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute top-0 right-1/4 w-24 h-24 bg-[#180c2e]/15 rounded-full blur-2xl animate-pulse delay-1000"></div>
        <div className="absolute bottom-0 left-1/2 transform -translate-x-1/2 w-40 h-20 bg-[#006da6]/10 rounded-full blur-3xl"></div>
      </div>

      <div className={`relative transition-all duration-700 ease-out app-bg-card app-border border ${
        isScrolled 
          ? 'backdrop-blur-2xl shadow-2xl' 
          : 'backdrop-blur-xl shadow-xl'
      } rounded-3xl overflow-visible`}>
        
        <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/5 via-transparent to-[#180c2e]/5 rounded-3xl"></div>
        
        <div className="relative w-full px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16 lg:h-18">
            
            <div className="flex-shrink-0">
              <Link 
                to="/" 
                className="flex items-center space-x-3 hover:opacity-90 transition-all duration-500 group"
              >
                <div className="relative">
                  <img 
                    src="/static/logo.svg" 
                    alt="NSWCC Logo" 
                    className="w-12 h-12 object-contain group-hover:scale-110 transition-transform duration-500 drop-shadow-lg"
                  />
                </div>
                <div className="block">
                  <h1 className="app-text-primary font-black text-xl leading-tight tracking-tight group-hover:text-[#006da6] transition-colors duration-300">
                    NSW Cleaning Company
                  </h1>
                  <p className="app-text-secondary text-xs font-semibold">NDIS APPROVED PROVIDER</p>
                </div>
              </Link>
            </div>
            <nav className="hidden lg:flex items-center space-x-1 app-bg-glass backdrop-blur-lg rounded-2xl px-3 py-1.5 app-border-glass border shadow-lg overflow-visible">
              <Link
                to="/"
                className={`px-4 py-2.5 text-sm font-bold transition-all duration-400 hover:scale-105 ${
                  isActivePath('/') 
                    ? 'px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu' 
                    : 'app-text-primary hover:text-[#006da6] hover:bg-white/60 dark:hover:bg-white/10 rounded-xl'
                }`}
              >
                Home
              </Link>

              <Link
                to="/about"
                className={`px-4 py-2.5 text-sm font-bold transition-all duration-400 hover:scale-105 ${
                  isActivePath('/about') 
                    ? 'px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu' 
                    : 'app-text-primary hover:text-[#006da6] hover:bg-white/60 dark:hover:bg-white/10 rounded-xl'
                }`}
              >
                About
              </Link>
              <div className="relative">
                <button
                  onClick={() => toggleDropdown('services')}
                  onMouseEnter={() => setActiveDropdown('services')}
                  className={`flex items-center px-4 py-2.5 text-sm font-bold transition-all duration-400 hover:scale-105 ${
                    isActivePath('/services') 
                      ? 'px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu' 
                      : 'app-text-primary hover:text-[#006da6] hover:bg-white/60 dark:hover:bg-white/10 rounded-xl'
                  }`}
                >
                  Services
                  <svg className={`ml-2 w-4 h-4 transition-transform duration-400 ${activeDropdown === 'services' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {activeDropdown === 'services' && (
                  <div 
                    className="absolute top-full left-0 mt-3 w-80 app-bg-card backdrop-blur-2xl rounded-3xl shadow-2xl app-border-glass border py-4 z-[9999] animate-in slide-in-from-top-3 duration-500"
                    onMouseLeave={() => setActiveDropdown(null)}
                  >
                    <div className="grid grid-cols-1 gap-1 px-3">
                      {servicesDropdown.map((item) => (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`flex items-center px-5 py-4 text-sm font-semibold transition-all duration-400 group hover:scale-105 ${
                            location.hash === item.path.split('#')[1] && isActivePath('/services')
                              ? 'bg-gradient-to-r from-[#006da6] to-[#180c2e] !text-white hover:!text-white rounded-2xl'
                              : 'app-text-secondary hover:bg-gradient-to-r hover:from-[#006da6]/10 hover:to-[#006da6]/5 hover:text-[#006da6] rounded-2xl'
                          }`}
                          onClick={() => setActiveDropdown(null)}
                        >
                          <span className="text-xl mr-4 group-hover:scale-125 transition-transform duration-400">{item.icon}</span>
                          {item.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <div className="relative">
                <button
                  onClick={() => toggleDropdown('resources')}
                  onMouseEnter={() => setActiveDropdown('resources')}
                  className={`flex items-center px-4 py-2.5 text-sm font-bold transition-all duration-400 hover:scale-105 ${
                    isActivePath('/faq') || isActivePath('/gallery') || isActivePath('/ndis') || isActivePath('/blog')
                      ? 'px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu' 
                      : 'app-text-primary hover:text-[#006da6] hover:bg-white/60 dark:hover:bg-white/10 rounded-xl'
                  }`}
                >
                  Resources
                  <svg className={`ml-2 w-4 h-4 transition-transform duration-400 ${activeDropdown === 'resources' ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
                
                {activeDropdown === 'resources' && (
                  <div 
                    className="absolute top-full left-0 mt-3 w-64 app-bg-card backdrop-blur-2xl rounded-3xl shadow-2xl app-border-glass border py-4 z-[9999] animate-in slide-in-from-top-3 duration-500"
                    onMouseLeave={() => setActiveDropdown(null)}
                  >
                    <div className="px-3">
                      {resourcesDropdown.map((item) => (
                        <Link
                          key={item.path}
                          to={item.path}
                          className={`flex items-center px-5 py-4 text-sm font-semibold transition-all duration-400 group hover:scale-105 ${
                            isActivePath(item.path)
                              ? 'bg-gradient-to-r from-[#006da6] to-[#180c2e] !text-white hover:!text-white rounded-2xl'
                              : 'app-text-secondary hover:bg-gradient-to-r hover:from-[#006da6]/10 hover:to-[#006da6]/5 hover:text-[#006da6] rounded-2xl'
                          }`}
                          onClick={() => setActiveDropdown(null)}
                        >
                          <span className="text-xl mr-4 group-hover:scale-125 transition-transform duration-400">{item.icon}</span>
                          {item.name}
                        </Link>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              <Link
                to="/contact"
                className={`px-4 py-2.5 text-sm font-bold transition-all duration-400 hover:scale-105 ${
                  isActivePath('/contact') 
                    ? 'px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu' 
                    : 'app-text-primary hover:text-[#006da6] hover:bg-white/60 dark:hover:bg-white/10 rounded-xl'
                }`}
              >
                Contact
              </Link>
            </nav>

            <div className="flex items-center space-x-3">
              <div className="hidden lg:flex items-center space-x-2">
                {showAuthButtons && user?.is_verified ? (
                  <div className="flex items-center space-x-2">
                    <Link
                      to="/clients/portal"
                      className={`px-4 py-2 text-sm font-semibold transition-colors duration-300 ${
                        isActivePath('/clients/portal')
                          ? 'px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu'
                          : 'app-text-primary hover:text-[#006da6]'
                      }`}
                    >
                      {user?.first_name || 'Portal'}
                    </Link>
                    <button
                      onClick={handleLogout}
                      className="px-4 py-2 text-sm font-semibold text-red-600 hover:text-red-500 transition-colors duration-300"
                    >
                      Logout
                    </button>
                  </div>
                ) : showAuthButtons && !user?.is_verified ? (
                  <div className="flex items-center space-x-2">
                    <span className="px-4 py-2 text-sm font-semibold text-orange-600">
                      Please verify your email
                    </span>
                    <button
                      onClick={handleLogout}
                      className="px-4 py-2 text-sm font-semibold text-red-600 hover:text-red-500 transition-colors duration-300"
                    >
                      Logout
                    </button>
                  </div>
                ) : !showAuthButtons ? (
                  <div className="flex items-center space-x-2">
                    <Link
                      to="/accounts/login"
                      className={`px-4 py-2 text-sm font-semibold transition-colors duration-300 ${
                        isActivePath('/accounts/login')
                          ? 'px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu'
                          : 'app-text-primary hover:text-[#006da6]'
                      }`}
                    >
                      Login
                    </Link>
                    <Link
                      to="/accounts/register"
                      className="px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white font-bold rounded-full transition-all duration-500 hover:scale-110 hover:shadow-2xl hover:-translate-y-1 transform-gpu"
                    >
                      <span className="!text-white hover:!text-white">Register</span>
                    </Link>
                  </div>
                ) : null}
                
                <button
                  onClick={() => window.location.href = '/quote'}
                  className="px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white font-bold rounded-full transition-all duration-500 hover:scale-110 hover:shadow-2xl hover:-translate-y-1 transform-gpu"
                >
                  <span className="!text-white hover:!text-white">Get Quote</span>
                </button>
              </div>

              <button
                onClick={toggleMenu}
                className="lg:hidden p-3 rounded-2xl app-text-secondary hover:app-text-primary hover:bg-white/60 dark:hover:bg-white/10 transition-all duration-400 hover:scale-110"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {isMenuOpen ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                  )}
                </svg>
              </button>
            </div>
          </div>

          {isMenuOpen && (
            <div className="lg:hidden app-bg-card backdrop-blur-2xl app-border-glass border-t rounded-b-3xl shadow-2xl mt-2">
              <div className="px-6 pt-6 pb-8 space-y-3">
                {NAVIGATION_LINKS.map((link) => (
                  <Link
                    key={link.path}
                    to={link.path}
                    className={`block px-6 py-4 text-base font-bold transition-all duration-400 hover:scale-105 ${
                      isActivePath(link.path)
                        ? 'bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu'
                        : 'app-text-primary hover:text-[#006da6] hover:bg-white/60 dark:hover:bg-white/10 rounded-2xl'
                    }`}
                    onClick={() => setIsMenuOpen(false)}
                  >
                    {link.name}
                  </Link>
                ))}
                
                <div className="pt-6 border-t app-border-glass mt-6 space-y-4">
                  {showAuthButtons && user?.is_verified ? (
                    <div className="space-y-3">
                      <Link
                        to="/clients/portal"
                        className={`block w-full px-6 py-3 text-center text-base font-bold transition-colors duration-300 ${
                          isActivePath('/clients/portal')
                            ? 'bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu'
                            : 'app-text-primary hover:text-[#006da6]'
                        }`}
                        onClick={() => setIsMenuOpen(false)}
                      >
                        {user?.first_name || 'Portal'}
                      </Link>
                      <button
                        onClick={() => {
                          handleLogout();
                          setIsMenuOpen(false);
                        }}
                        className="block w-full px-6 py-3 text-center text-base font-bold text-red-600 hover:text-red-500 transition-colors duration-300"
                      >
                        Logout
                      </button>
                    </div>
                  ) : showAuthButtons && !user?.is_verified ? (
                    <div className="space-y-3">
                      <span className="block w-full px-6 py-3 text-center text-base font-bold text-orange-600">
                        Please verify your email
                      </span>
                      <button
                        onClick={() => {
                          handleLogout();
                          setIsMenuOpen(false);
                        }}
                        className="block w-full px-6 py-3 text-center text-base font-bold text-red-600 hover:text-red-500 transition-colors duration-300"
                      >
                        Logout
                      </button>
                    </div>
                  ) : !showAuthButtons ? (
                    <div className="space-y-3">
                      <Link
                        to="/accounts/login"
                        className={`block w-full px-6 py-3 text-center text-base font-bold transition-colors duration-300 ${
                          isActivePath('/accounts/login')
                            ? 'bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white rounded-full hover:shadow-2xl hover:-translate-y-1 transform-gpu'
                            : 'app-text-primary hover:text-[#006da6]'
                        }`}
                        onClick={() => setIsMenuOpen(false)}
                      >
                        Login
                      </Link>
                      <Link
                        to="/accounts/register"
                        className="block w-full px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white font-bold rounded-full transition-all duration-500 hover:scale-110 hover:shadow-2xl hover:-translate-y-1 transform-gpu text-center py-3"
                        onClick={() => setIsMenuOpen(false)}
                      >
                        <span className="!text-white hover:!text-white">Register</span>
                      </Link>
                    </div>
                  ) : null}
                  
                  <button
                    onClick={() => window.location.href = '/quote'}
                    className="w-full px-6 bg-gradient-to-r from-[#006da6] to-[#180c2e] hover:from-[#180c2e] hover:to-[#2d1b4e] !text-white hover:!text-white font-bold rounded-full transition-all duration-500 hover:scale-110 hover:shadow-2xl hover:-translate-y-1 transform-gpu py-3"
                  >
                    <span className="!text-white hover:!text-white">Get Free Quote</span>
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default Header;

