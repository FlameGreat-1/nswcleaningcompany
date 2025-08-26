import React, { useState, useRef, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { Link } from 'react-router-dom';

const Avatar = React.forwardRef(({ className, children, ...props }, ref) => {
  return (
    <div
      ref={ref}
      className={`relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full transition-all duration-300 ease-in-out hover:scale-105 ring-2 ring-white dark:ring-gray-800 shadow-lg ${className || ''}`}
      {...props}
    >
      {children}
    </div>
  );
});

const AvatarImage = React.forwardRef(({ className, src, alt, ...props }, ref) => {
  return (
    <img
      ref={ref}
      src="https://api.dicebear.com/7.x/personas/svg?seed=professional&backgroundColor=1e40af&radius=50"
      alt={alt || "Avatar"}
      className={`aspect-square h-full w-full object-cover ${className || ''}`}
      {...props}
    />
  );
});

const AvatarFallback = React.forwardRef(({ className, children, status, ...props }, ref) => {
  const getStatusColor = () => {
    switch (status) {
      case 'online': return 'bg-emerald-500 ring-emerald-100';
      case 'away': return 'bg-amber-500 ring-amber-100';
      case 'busy': return 'bg-red-500 ring-red-100';
      case 'offline': return 'bg-gray-400 ring-gray-100';
      default: return 'bg-gray-400 ring-gray-100';
    }
  };

  return (
    <div
      ref={ref}
      className={`flex h-full w-full items-center justify-center rounded-full bg-gradient-to-br from-blue-600 to-blue-700 text-white font-bold text-sm shadow-inner ${className || ''}`}
      {...props}
    >
      {children}
      {status && (
        <div className={`absolute -bottom-0.5 -right-0.5 h-3.5 w-3.5 rounded-full border-2 border-white dark:border-gray-800 ${getStatusColor()} shadow-sm`}></div>
      )}
    </div>
  );
});

const ProfileAvatar = () => {
  const { user, logout, isVerified } = useAuth();
  const { isDark } = useTheme();
  const [isOpen, setIsOpen] = useState(false);
  const dropdownRef = useRef(null);

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
  };

  const toggleDropdown = () => {
    setIsOpen(!isOpen);
  };

  const getInitials = () => {
    if (!user) return 'U';
    const firstName = user.first_name || '';
    const lastName = user.last_name || '';
    return `${firstName.charAt(0)}${lastName.charAt(0)}`.toUpperCase() || user.email?.charAt(0).toUpperCase() || 'U';
  };

  const getStatusIndicator = () => {
    if (!user) return 'offline';
    if (isVerified) return 'online';
    return 'away';
  };

  const getStatusText = () => {
    if (!user) return 'Offline';
    if (isVerified) return 'Active';
    return 'Pending Verification';
  };

  const getStatusColor = () => {
    if (!user) return 'text-gray-500';
    if (isVerified) return 'text-green-600';
    return 'text-yellow-600';
  };

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  if (!user) return null;

  return (
    <div className="relative" ref={dropdownRef}>
      <Avatar className="cursor-pointer" onClick={toggleDropdown}>
        <AvatarImage alt={`${user.first_name} ${user.last_name}`} />
        <AvatarFallback status={getStatusIndicator()}>
          {getInitials()}
        </AvatarFallback>
      </Avatar>

      {isOpen && (
        <div className={`absolute right-0 mt-2 w-80 rounded-xl shadow-2xl border z-50 ${isDark ? 'bg-[#1a0f33] border-gray-700' : 'bg-white border-gray-200'}`}>
          <div className="p-4">
            <div className="flex items-center space-x-3 mb-4">
              <Avatar className="h-12 w-12">
                <AvatarImage alt={`${user.first_name} ${user.last_name}`} />
                <AvatarFallback status={getStatusIndicator()}>
                  {getInitials()}
                </AvatarFallback>
              </Avatar>
              <div className="flex-1 min-w-0">
                <p className={`font-semibold truncate ${isDark ? 'text-white' : 'text-gray-900'}`}>
                  {user.first_name} {user.last_name}
                </p>
                <p className={`text-sm truncate ${isDark ? 'text-gray-400' : 'text-gray-600'}`}>
                  {user.email}
                </p>
                <div className="flex items-center space-x-1 mt-1">
                  <div className={`h-2 w-2 rounded-full ${getStatusIndicator() === 'online' ? 'bg-green-500' : getStatusIndicator() === 'away' ? 'bg-yellow-500' : 'bg-gray-400'}`}></div>
                  <span className={`text-xs font-medium ${getStatusColor()}`}>
                    {getStatusText()}
                  </span>
                </div>
              </div>
            </div>

            <div className={`border-t pt-3 ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
              <div className="space-y-1">
                <div className={`px-3 py-2 rounded-lg ${isDark ? 'bg-blue-900/20' : 'bg-blue-50'}`}>
                  <div className="flex items-center justify-between">
                    <span className={`text-sm font-medium ${isDark ? 'text-blue-400' : 'text-blue-700'}`}>
                      Account Type
                    </span>
                    <span className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-blue-800 text-blue-200' : 'bg-blue-100 text-blue-800'}`}>
                      {user.client_type === 'ndis' ? 'NDIS Client' : 'General Client'}
                    </span>
                  </div>
                </div>

                {!isVerified && (
                  <div className={`px-3 py-2 rounded-lg ${isDark ? 'bg-yellow-900/20' : 'bg-yellow-50'}`}>
                    <div className="flex items-center space-x-2">
                      <svg className={`w-4 h-4 ${isDark ? 'text-yellow-400' : 'text-yellow-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                      </svg>
                      <span className={`text-xs ${isDark ? 'text-yellow-400' : 'text-yellow-700'}`}>
                        Email verification pending
                      </span>
                    </div>
                  </div>
                )}
              </div>
            </div>

            <div className={`border-t pt-3 mt-3 ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
              <div className="space-y-1">
                <div
                  className={`flex items-center space-x-3 px-3 py-2 rounded-lg ${isDark ? 'text-gray-500 cursor-not-allowed' : 'text-gray-400 cursor-not-allowed'}`}
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 7a2 2 0 012 2m0 0a2 2 0 012 2v6a2 2 0 01-2 2H9a2 2 0 01-2-2V9a2 2 0 012-2m0 0V7a2 2 0 012-2m0 0V5a2 2 0 012-2h4a2 2 0 012 2v2M9 7h6" />
                  </svg>
                  <span className="text-sm font-medium">Change Password</span>
                </div>

                <div
                  className={`flex items-center justify-between px-3 py-2 rounded-lg ${isDark ? 'bg-gray-800 text-gray-300' : 'bg-gray-100 text-gray-700'}`}
                >
                  <div className="flex items-center space-x-3">
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                    <span className="text-sm font-medium">Account Settings</span>
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-full ${isDark ? 'bg-blue-900 text-blue-300' : 'bg-blue-100 text-blue-700'}`}>
                    Coming Soon
                  </span>
                </div>
              </div>
            </div>

            <div className={`border-t pt-3 mt-3 ${isDark ? 'border-gray-700' : 'border-gray-200'}`}>
              <button
                onClick={handleLogout}
                className={`flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors w-full text-left ${isDark ? 'hover:bg-red-900/20 text-red-400 hover:text-red-300' : 'hover:bg-red-50 text-red-600 hover:text-red-700'}`}
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
                </svg>
                <span className="text-sm font-medium">Sign Out</span>
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProfileAvatar;
