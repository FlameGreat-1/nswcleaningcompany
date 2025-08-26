import { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate, useLocation, useSearchParams } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import { redirectAfterLogin } from '../../utils/auth';
import EmailVerificationForm from '../../components/accounts/forms/EmailVerificationForm';

const EmailVerification = () => {
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  
  const { isAuthenticated, user, isVerified } = useAuth();
  const { isDark } = useTheme();
  const navigate = useNavigate();
  const location = useLocation();
  const [searchParams] = useSearchParams();

  const token = searchParams.get('token');
  const userEmail = location.state?.email || user?.email || '';
  const message = location.state?.message || '';

  useEffect(() => {
    if (isAuthenticated && user && isVerified) {
      const redirectPath = redirectAfterLogin(user.user_type);
      navigate(redirectPath, { replace: true });
    }
  }, [isAuthenticated, user, isVerified, navigate]);

  useEffect(() => {
    if (message) {
      setSuccess(message);
    }
  }, [message]);

  const handleVerificationSuccess = useCallback((response) => {
    if (token) {
      setSuccess('Email verified successfully!');
      setError('');
      setTimeout(() => {
        if (isAuthenticated && user) {
          const redirectPath = redirectAfterLogin(user.user_type);
          navigate(redirectPath, { replace: true });
        } else {
          navigate('/accounts/login?message=email_verified', { replace: true });
        }
      }, 2000);
    } else {
      setSuccess('Verification email sent successfully! Please check your inbox.');
      setError('');
    }
  }, [token, isAuthenticated, user, navigate]);

  const handleVerificationError = useCallback((errorMessage) => {
    setError(errorMessage);
    setSuccess('');
  }, []);

  const handleBackToLogin = useCallback(() => {
    if (isAuthenticated && user) {
      const redirectPath = redirectAfterLogin(user.user_type);
      navigate(redirectPath, { replace: true });
    } else {
      navigate('/accounts/login');
    }
  }, [isAuthenticated, user, navigate]);

  const getPageTitle = () => {
    return token ? 'Verify Your Email' : 'Email Verification';
  };

  const getPageDescription = () => {
    return token 
      ? 'Confirming your email address'
      : 'Check your inbox for the verification link';
  };

  return (
    <div className={`min-h-screen relative overflow-hidden ${
      isDark ? 'bg-gradient-to-br from-[#180c2e] via-[#2d1b4e] to-[#180c2e]' : 'bg-gradient-to-br from-gray-50 via-white to-gray-100'
    }`}>
      <div className="absolute inset-0">
        <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-[#006da6]/5 rounded-full blur-3xl animate-pulse"></div>
        <div className="absolute bottom-1/4 right-1/4 w-80 h-80 bg-[#005a8a]/3 rounded-full blur-3xl animate-pulse delay-1000"></div>
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-[500px] h-[500px] bg-gradient-to-r from-[#006da6]/3 to-[#005a8a]/3 rounded-full blur-3xl animate-spin-slow"></div>
      </div>

      <div className="relative z-10 min-h-screen flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-md w-full space-y-8 animate-fade-in-up">
          <div className="text-center space-y-6">
            <div className="relative group">
              <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/20 to-[#005a8a]/20 rounded-2xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
              <Link to="/" className="relative inline-block transform hover:scale-105 transition-transform duration-300">
                <img
                  src="/logo.svg"
                  alt="NSWCC Logo"
                  className="h-12 w-auto mx-auto filter drop-shadow-lg"
                />
              </Link>
            </div>
            
            <div className="space-y-3">
              <h2 className={`text-4xl font-black bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent animate-fade-in-up delay-200`}>
                {getPageTitle()}
              </h2>
              <p className={`text-base font-medium animate-fade-in-up delay-300 ${
                isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'
              }`}>
                {getPageDescription()}
              </p>
            </div>
          </div>

          <div className="relative group animate-fade-in-up delay-400">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-3xl blur opacity-20 group-hover:opacity-30 transition-all duration-700"></div>
            <div className={`relative backdrop-blur-xl rounded-3xl p-8 border-2 transition-all duration-700 hover:-translate-y-2 hover:scale-[1.02] transform-gpu ${
              isDark 
                ? 'bg-white/5 border-white/20 hover:bg-white/10 hover:border-[#006da6]/30' 
                : 'bg-white/90 border-white/40 hover:bg-white hover:border-[#006da6]/30'
            }`}>
              <div className="absolute inset-0 bg-gradient-to-br from-[#006da6]/5 via-transparent to-[#005a8a]/5 opacity-0 group-hover:opacity-100 transition-opacity duration-700 rounded-3xl"></div>
              
              <div className="relative z-10">
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

                <EmailVerificationForm
                  token={token}
                  userEmail={userEmail}
                  onSuccess={handleVerificationSuccess}
                  onError={handleVerificationError}
                  onBackToLogin={handleBackToLogin}
                />
              </div>
            </div>
          </div>

          {!token && (
            <div className="text-center animate-fade-in-up delay-600">
              <div className={`relative inline-block p-4 rounded-2xl backdrop-blur-xl transition-all duration-300 hover:scale-105 ${
                isDark ? 'bg-white/5 border border-white/20' : 'bg-white/50 border border-white/40'
              }`}>
                <p className={`text-sm font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
                  Need help?{' '}
                  <Link
                    to="/accounts/login"
                    className="font-black text-[#006da6] hover:text-[#0080c7] hover:underline transition-all duration-300 hover:scale-105 inline-block"
                  >
                    Back to Sign In
                  </Link>
                </p>
              </div>
            </div>
          )}

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

      <div className="absolute bottom-0 left-0 right-0 h-32 bg-gradient-to-t from-black/20 to-transparent pointer-events-none"></div>
    </div>
  );
};

export default EmailVerification;
