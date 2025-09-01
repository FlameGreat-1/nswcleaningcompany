import { useState, useEffect } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { redirectAfterLogin } from '../../utils/auth';
import LoginForm from '../../components/accounts/forms/LoginForm';

const Login = () => {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const { isAuthenticated, user } = useAuth();
  const { isDark } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/';
  const userType = new URLSearchParams(location.search).get('type') || 'client';
  const clientType = new URLSearchParams(location.search).get('client_type') || 'general';

  useEffect(() => {
    if (isAuthenticated && user) {
      const redirectPath = redirectAfterLogin(user.user_type);
      navigate(redirectPath, { replace: true });
    }
  }, [isAuthenticated, user, navigate]);

  useEffect(() => {
    const message = new URLSearchParams(location.search).get('message');
    if (message) {
      if (message === 'registration_success') {
        setSuccess('Registration successful! Please sign in to continue.');
      } else if (message === 'password_reset_success') {
        setSuccess('Password reset successful! Please sign in with your new password.');
      } else if (message === 'email_verified') {
        setSuccess('Email verified successfully! Please sign in to continue.');
      }
    }
  }, [location.search]);

  const handleLoginSuccess = (response) => {
    const redirectPath = response.redirectTo || redirectAfterLogin(response.user.user_type);
    navigate(redirectPath, { replace: true });
  };
  
  const handleLoginError = (errorMessage) => {
    setError(errorMessage);
    setSuccess('');
  };
  
  const handleForgotPassword = () => {
    navigate('/accounts/password-reset');
  };
  
  if (isAuthenticated) {
    return null;
  }
  
  return (
    <div className={`min-h-screen relative overflow-hidden ${
      isDark ? 'bg-gradient-to-br from-[#180c2e] via-[#2d1b4e] to-[#180c2e]' : 'bg-gradient-to-br from-gray-50 via-white to-gray-100'
    }`}>
      {/* Background Effects */}
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#005a8a]/3 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/3 to-[#005a8a]/3 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 animate-fade-in-up">
          {/* Header */}
          <div className="text-center space-y-6">
            <div className="relative group">
              <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/20 to-[#005a8a]/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
              <Link to="/" className="relative inline-block transform hover:scale-105 transition-transform duration-300">
                <img
                  src="/static/logo.svg"
                  alt="NSWCC Logo"
                  className="h-12 w-auto mx-auto filter drop-shadow-lg"
                />
              </Link>
            </div>
            
            <div className="space-y-3">
              <h2 className={`text-4xl font-black bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent animate-fade-in-up delay-200`}>
                Welcome Back
              </h2>
              <p className={`text-base font-medium animate-fade-in-up delay-300 ${
                isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'
              }`}>
                Sign in to your account to continue
              </p>
            </div>
          </div>

          {/* Main Form Card */}
          <div className="relative group animate-fade-in-up delay-400">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-20 group-hover:opacity-30 transition-all duration-700"></div>
            <div className={`relative backdrop-blur-xl rounded-3xl p-8 border-2 transition-all duration-700 hover:-translate-y-2 hover:scale-[1.02] transform-gpu ${
              isDark 
                ? 'bg-white/5 border-white/20 hover:bg-white/10 hover:border-[#006da6]/30' 
                : 'bg-white/90 border-white/40 hover:bg-white hover:border-[#006da6]/30'
            }`}>
              <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
              
              <div className="relative z-10">
                {/* Success Message */}
                {success && (
                  <div className={`mb-6 p-4 rounded-xl border-2 animate-fade-in-up ${
                    isDark 
                      ? 'bg-green-500/10 border-green-500/30 backdrop-blur-xl' 
                      : 'bg-green-50 border-green-200'
                  }`}>
                    <div className="absolute -inset-1 bg-gradient-to-r from-green-500/20 to-green-600/20 rounded-xl blur opacity-50"></div>
                    <p className="relative text-sm text-green-500 font-semibold">{success}</p>
                  </div>
                )}

                {/* Error Message */}
                {error && (
                  <div className={`mb-6 p-4 rounded-xl border-2 animate-fade-in-up ${
                    isDark 
                      ? 'bg-red-500/10 border-red-500/30 backdrop-blur-xl' 
                      : 'bg-red-50 border-red-200'
                  }`}>
                    <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 to-red-600/20 rounded-xl blur opacity-50"></div>
                    <p className="relative text-sm text-red-500 font-semibold">{error}</p>
                  </div>
                )}

                <LoginForm
                  onSuccess={handleLoginSuccess}
                  onError={handleLoginError}
                  onForgotPassword={handleForgotPassword}
                  userType={userType}
                  clientType={clientType}
                />
              </div>
            </div>
          </div>

          {/* Register Link */}
          <div className="text-center animate-fade-in-up delay-600">
            <div className={`relative inline-block p-4 rounded-2xl backdrop-blur-xl transition-all duration-300 hover:scale-105 ${
              isDark ? 'bg-white/5 border border-white/20' : 'bg-white/50 border border-white/40'
            }`}>
              <p className={`text-sm font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
                Don't have an account?{' '}
                <Link
                  to={`/accounts/register${userType !== 'client' ? `?type=${userType}` : ''}${
                    clientType !== 'general' ? `${userType !== 'client' ? '&' : '?'}client_type=${clientType}` : ''
                  }`}
                  className="font-black text-[#006da6] hover:text-[#0080c7] hover:underline transition-all duration-300 hover:scale-105 inline-block"
                >
                  Sign up here
                </Link>
              </p>
            </div>
          </div>

          {/* Back to Home Link */}
          <div className="text-center animate-fade-in-up delay-700">
            <Link
              to="/"
              className={`inline-flex items-center gap-2 text-sm font-semibold transition-all duration-300 hover:scale-105 p-3 rounded-xl backdrop-blur-xl ${
                isDark 
                  ? 'text-[#CCCCCC] hover:text-[#006da6] hover:bg-white/10 border border-white/20' 
                  : 'text-[#6B7280] hover:text-[#006da6] hover:bg-white/50 border border-white/40'
              }`}
            >
              <svg className="w-4 h-4 transition-transform duration-300 group-hover:-translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
              </svg>
              Back to Home
            </Link>
          </div>
        </div>
      </div>

      {/* Bottom Gradient */}
      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/20 to-transparent pointer-events-none"></div>
    </div>
  );
};

export default Login;
