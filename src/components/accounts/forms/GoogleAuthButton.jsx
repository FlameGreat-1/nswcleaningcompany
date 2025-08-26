import { useState } from 'react';
import { useGoogleAuth } from '../../../hooks/useAuth';
import { useTheme } from '../../../contexts/ThemeContext';
import LoadingSpinner from '../../common/LoadingSpinner';

const GoogleAuthButton = ({ 
  mode = 'login',
  userType = 'client',
  clientType = 'general',
  phoneNumber = '',
  onSuccess,
  onError,
  className = '',
  disabled = false,
  size = 'md'
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const { googleLogin, googleRegister, error } = useGoogleAuth();
  const { isDark } = useTheme();

  const sizeClasses = {
    sm: 'px-4 py-2 text-sm',
    md: 'px-6 py-3 text-base',
    lg: 'px-8 py-4 text-lg'
  };

  const handleGoogleAuth = async () => {
    if (disabled || isLoading) return;
  
    setIsLoading(true);
  
    try {
      let response;
      
      if (mode === 'register') {
        response = await googleRegister(userType, clientType, phoneNumber);
      } else {
        response = await googleLogin(userType, clientType);
      }
      
      if (!response.success && response.accountExists) {
        onError?.(response.error || 'This email is already registered. Please sign in instead.');
        return;
      }
      
      if (response.success || response.token || (response.user && response.user.id)) {
        onSuccess?.(response);
      } else {
        onError?.(response.error || 'Google authentication failed');
      }
    } catch (err) {
      onError?.(err.message || 'Google authentication failed');
    } finally {
      setIsLoading(false);
    }
  };
  
  const buttonText = mode === 'register' ? 'Sign up with Google' : 'Sign in with Google';

  return (
    <div className="relative group">
      <div className="absolute -inset-1 bg-gradient-to-r from-[#4285F4]/20 via-[#34A853]/20 to-[#EA4335]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
      <button
        type="button"
        onClick={handleGoogleAuth}
        disabled={disabled || isLoading}
        className={`
          relative w-full flex items-center justify-center gap-3 
          ${sizeClasses[size]}
          backdrop-blur-xl border-2 rounded-xl font-semibold
          transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1
          disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:translate-y-0
          focus:outline-none focus:ring-4 focus:ring-[#4285F4]/20
          overflow-hidden
          ${isDark 
            ? 'bg-white/5 border-white/20 text-white hover:bg-white/10 hover:border-white/30' 
            : 'bg-white/90 border-gray-200 text-[#180c2e] hover:bg-white hover:border-gray-300'
          }
          ${className}
        `}
      >
        <div className="absolute inset-0 bg-gradient-to-r from-[#4285F4]/5 via-[#34A853]/5 to-[#EA4335]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
        
        <div className="relative z-10 flex items-center justify-center gap-3">
          {isLoading ? (
            <LoadingSpinner size="sm" color="primary" />
          ) : (
            <svg
              className="w-5 h-5 transition-transform duration-300 group-hover:scale-110"
              viewBox="0 0 24 24"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fill="#4285F4"
                d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
              />
              <path
                fill="#34A853"
                d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
              />
              <path
                fill="#FBBC05"
                d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
              />
              <path
                fill="#EA4335"
                d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
              />
            </svg>
          )}
          
          <span className="font-black transition-colors duration-300">
            {isLoading ? 'Authenticating...' : buttonText}
          </span>
        </div>
      </button>
    </div>
  );
};

export default GoogleAuthButton;