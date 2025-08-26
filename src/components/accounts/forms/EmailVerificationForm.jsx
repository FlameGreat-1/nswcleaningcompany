import { useState, useEffect, useRef, useCallback } from 'react';
import { useEmailVerification } from '../../../hooks/useAuth';
import { useTheme } from '../../../contexts/ThemeContext';
import { validateEmail } from '../../../utils/auth';
import LoadingSpinner from '../../common/LoadingSpinner';

const EmailVerificationForm = ({ 
  token,
  userEmail,
  onSuccess, 
  onError,
  onBackToLogin,
  className = '' 
}) => {
  const [email, setEmail] = useState(userEmail || '');
  const [errors, setErrors] = useState({});
  const [isVerified, setIsVerified] = useState(false);
  const [autoVerifying, setAutoVerifying] = useState(!!token);
  const [focusedFields, setFocusedFields] = useState({});
  
  const verificationAttempted = useRef(false);

  const { verifyEmail, resendVerification, loading, error, setError } = useEmailVerification();
  const { isDark } = useTheme();

  const handleTokenVerification = useCallback(async () => {
    if (verificationAttempted.current) {
      return;
    }
    
    verificationAttempted.current = true;
    setAutoVerifying(true);
    
    try {
      const timeoutPromise = new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Verification timeout')), 30000)
      );
      
      const response = await Promise.race([
        verifyEmail(token),
        timeoutPromise
      ]);
      
      if (response?.success) {
        setIsVerified(true);
        
        if (window.history.replaceState) {
          const url = new URL(window.location);
          url.searchParams.delete('token');
          window.history.replaceState({}, '', url);
        }
        
        onSuccess?.(response);
      } else {
        onError?.(response?.error || 'Email verification failed');
      }
    } catch (err) {
      const errorMessage = err.message === 'Verification timeout' 
        ? 'Verification timed out. Please try again.' 
        : 'Email verification failed. Please try again.';
      onError?.(errorMessage);
    } finally {
      setAutoVerifying(false);
    }
  }, [token, verifyEmail, onSuccess, onError]);

  useEffect(() => {
    if (token && 
        token.length > 10 && 
        !isVerified && 
        !verificationAttempted.current) {
      handleTokenVerification();
    }
  }, [token, isVerified, handleTokenVerification]);
  
  useEffect(() => {
    return () => {
      if (verificationAttempted.current) {
        verificationAttempted.current = true;
      }
    };
  }, []);
  
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (document.hidden && verificationAttempted.current) {
        return;
      }
    };
  
    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);
  
  useEffect(() => {
    if (token && token.length > 10) {
      const handleBeforeUnload = () => {
        verificationAttempted.current = true;
      };
      
      const handleFocus = () => {
        if (verificationAttempted.current && isVerified) {
          window.close();
        }
      };
  
      window.addEventListener('beforeunload', handleBeforeUnload);
      window.addEventListener('focus', handleFocus);
      
      return () => {
        window.removeEventListener('beforeunload', handleBeforeUnload);
        window.removeEventListener('focus', handleFocus);
      };
    }
  }, [token, isVerified]);

  const handleInputChange = (e) => {
    setEmail(e.target.value);
    
    if (errors.email) {
      setErrors(prev => ({ ...prev, email: '' }));
    }
    if (error) {
      setError(null);
    }
  };

  const handleFocus = (fieldName) => {
    setFocusedFields(prev => ({ ...prev, [fieldName]: true }));
  };

  const handleBlur = (fieldName) => {
    if (!email) {
      setFocusedFields(prev => ({ ...prev, [fieldName]: false }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleResendVerification = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    const response = await resendVerification(email.trim());

    if (response.success) {
      onSuccess?.(response);
    } else {
      onError?.(response.error || 'Failed to resend verification email');
    }
  };

  const getInputClasses = (fieldName, hasError = false) => {
    const baseClasses = `
      w-full px-4 pt-6 pb-2 rounded-xl border-2 transition-all duration-300
      font-medium text-base backdrop-blur-xl
      focus:outline-none focus:ring-4 focus:scale-[1.02] transform-gpu
      ${isDark 
        ? 'bg-white/5 border-white/20 text-white focus:border-[#006da6] focus:ring-[#006da6]/20 focus:bg-white/10' 
        : 'bg-white/90 border-gray-200 text-[#180c2e] focus:border-[#006da6] focus:ring-[#006da6]/20 focus:bg-white'
      }
    `;
    
    const errorClasses = hasError ? `
      border-red-500 focus:border-red-500 focus:ring-red-500/20
      ${isDark ? 'bg-red-500/5' : 'bg-red-50'}
    ` : '';

    return `${baseClasses} ${errorClasses}`.trim();
  };

  const getLabelClasses = (fieldName, hasError = false) => {
    const isActive = focusedFields[fieldName] || email;
    const baseClasses = `
      absolute left-4 transition-all duration-300 pointer-events-none font-semibold
      ${isActive 
        ? 'top-2 text-xs' 
        : 'top-1/2 transform -translate-y-1/2 text-base'
      }
      ${hasError 
        ? 'text-red-500' 
        : isActive 
          ? 'text-[#006da6]'
          : (isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]')
      }
    `;
    
    return baseClasses.trim();
  };

  if (autoVerifying) {
    return (
      <div className={`text-center space-y-8 animate-fade-in-up ${className}`}>
        <div className="flex justify-center">
          <div className="relative">
            <div className="absolute -inset-4 bg-gradient-to-r from-[#006da6]/20 to-[#005a8a]/20 rounded-full blur animate-pulse"></div>
            <LoadingSpinner size="lg" color="primary" />
          </div>
        </div>

        <div className="space-y-4">
          <h3 className={`text-2xl font-black bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent`}>
            Verifying Your Email
          </h3>
          <p className={`text-base font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
            Please wait while we verify your email address...
          </p>
        </div>
      </div>
    );
  }

  if (isVerified) {
    return (
      <div className={`text-center space-y-8 animate-fade-in-up ${className}`}>
        <div className="flex justify-center">
          <div className="relative group">
            <div className="absolute -inset-2 bg-gradient-to-r from-green-500/30 to-green-600/30 rounded-full blur opacity-50 animate-pulse"></div>
            <div className={`relative w-20 h-20 rounded-full flex items-center justify-center backdrop-blur-xl border-2 ${
              isDark 
                ? 'bg-green-500/10 border-green-500/30' 
                : 'bg-green-50 border-green-200'
            }`}>
              <svg 
                className="w-10 h-10 text-green-500 animate-bounce" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={3} 
                  d="M5 13l4 4L19 7" 
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className={`text-2xl font-black bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent`}>
            Email Verified Successfully
          </h3>
          <p className={`text-base font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
            Your email address has been verified. You can now access all features of your account.
          </p>
        </div>

        {onBackToLogin && (
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-xl blur opacity-0 group-hover:opacity-30 transition-all duration-300"></div>
            <button
              type="button"
              onClick={onBackToLogin}
              className="relative w-full bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:via-[#2d1b4e] hover:to-[#180c2e] text-white font-black py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-[#006da6]/20 backdrop-blur-xl overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <span className="relative z-10">Continue to Dashboard</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  if (token && !isVerified) {
    return (
      <div className={`text-center space-y-8 animate-fade-in-up ${className}`}>
        <div className="flex justify-center">
          <div className="relative group">
            <div className="absolute -inset-2 bg-gradient-to-r from-red-500/30 to-red-600/30 rounded-full blur opacity-50 animate-pulse"></div>
            <div className={`relative w-20 h-20 rounded-full flex items-center justify-center backdrop-blur-xl border-2 ${
              isDark 
                ? 'bg-red-500/10 border-red-500/30' 
                : 'bg-red-50 border-red-200'
            }`}>
              <svg 
                className="w-10 h-10 text-red-500 animate-bounce" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={3} 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" 
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="space-y-4">
          <h3 className={`text-2xl font-black bg-gradient-to-r from-red-500 to-red-600 bg-clip-text text-transparent`}>
            Verification Failed
          </h3>
          <p className={`text-base font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
            This verification link is invalid or has expired. Please request a new verification email.
          </p>
        </div>

        <form onSubmit={handleResendVerification} className="space-y-5">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
            <div className="relative">
              <input
                id="email"
                name="email"
                type="email"
                autoComplete="email"
                required
                value={email}
                onChange={handleInputChange}
                onFocus={() => handleFocus('email')}
                onBlur={() => handleBlur('email')}
                className={getInputClasses('email', errors.email)}
                disabled={loading}
              />
              <label 
                htmlFor="email" 
                className={getLabelClasses('email', errors.email)}
              >
                Email Address
              </label>
            </div>
            {errors.email && (
              <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.email}</p>
            )}
          </div>

          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] rounded-xl blur opacity-0 group-hover:opacity-30 transition-all duration-300"></div>
            <button
              type="submit"
              disabled={loading}
              className="relative w-full bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] hover:from-[#180c2e] hover:via-[#2d1b4e] hover:to-[#180c2e] text-white font-black py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-[#006da6]/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:translate-y-0 backdrop-blur-xl overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
              <div className="relative z-10">
                {loading ? (
                  <div className="flex items-center justify-center gap-3">
                    <LoadingSpinner size="sm" color="white" />
                    <span>Sending Verification Email...</span>
                  </div>
                ) : (
                  'Send New Verification Email'
                )}
              </div>
            </button>
          </div>
        </form>

        {onBackToLogin && (
          <div className="text-center">
            <div className="relative group inline-block">
              <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/20 to-[#005a8a]/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
              <button
                type="button"
                onClick={onBackToLogin}
                className={`relative text-sm font-black transition-all duration-300 hover:scale-105 p-3 rounded-lg backdrop-blur-xl ${
                  isDark 
                    ? 'text-[#006da6] hover:text-[#0080c7] hover:bg-white/10 border border-white/20' 
                    : 'text-[#006da6] hover:text-[#0080c7] hover:bg-[#006da6]/10 border border-gray-200'
                }`}
                disabled={loading}
              >
                Back to Sign In
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`space-y-6 animate-fade-in-up ${className}`}>
      <div className="text-center space-y-6">
        <div className="flex justify-center">
          <div className="relative group">
            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/20 to-[#005a8a]/20 rounded-full blur opacity-50 animate-pulse"></div>
            <div className={`relative w-20 h-20 rounded-full flex items-center justify-center backdrop-blur-xl border-2 ${
              isDark 
                ? 'bg-[#006da6]/10 border-[#006da6]/30' 
                : 'bg-[#006da6]/5 border-[#006da6]/20'
            }`}>
              <svg 
                className="w-10 h-10 text-[#006da6] animate-pulse" 
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" 
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <h2 className={`text-3xl font-black bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent`}>
            Verify Your Email
          </h2>
          <p className={`text-base font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
            We've sent a verification email to your address. Please check your inbox and click the verification link.
          </p>
        </div>
      </div>

      {error && (
        <div className={`relative group p-4 rounded-xl border-2 animate-fade-in-up ${
          isDark 
            ? 'bg-red-500/10 border-red-500/30 backdrop-blur-xl' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 to-red-600/20 rounded-xl blur opacity-50"></div>
          <p className="relative text-sm text-red-500 font-semibold">{error}</p>
        </div>
      )}

      <form onSubmit={handleResendVerification} className="space-y-5">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={email}
              onChange={handleInputChange}
              onFocus={() => handleFocus('email')}
              onBlur={() => handleBlur('email')}
              className={getInputClasses('email', errors.email)}
              disabled={loading}
            />
            <label 
              htmlFor="email" 
              className={getLabelClasses('email', errors.email)}
            >
              Email Address
            </label>
          </div>
          {errors.email && (
            <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.email}</p>
          )}
        </div>

        <div className="space-y-4">
          <div className="relative group">
            <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/30 to-[#005a8a]/30 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
            <button
              type="submit"
              disabled={loading}
              className={`relative w-full backdrop-blur-xl border-2 font-black py-4 px-6 rounded-xl transition-all duration-300 transform hover:scale-[1.02] hover:-translate-y-1 focus:outline-none focus:ring-4 focus:ring-[#006da6]/20 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 disabled:hover:translate-y-0 ${
                isDark 
                  ? 'bg-white/5 border-[#006da6] text-[#006da6] hover:bg-[#006da6] hover:text-white hover:border-[#006da6]' 
                  : 'bg-white/90 border-[#006da6] text-[#006da6] hover:bg-[#006da6] hover:text-white hover:border-[#006da6]'
              }`}
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[#006da6]/10 to-[#005a8a]/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl"></div>
              <div className="relative z-10">
                {loading ? (
                  <div className="flex items-center justify-center gap-3">
                    <LoadingSpinner size="sm" color="primary" />
                    <span>Sending Verification Email...</span>
                  </div>
                ) : (
                  'Resend Verification Email'
                )}
              </div>
            </button>
          </div>

          {onBackToLogin && (
            <div className="text-center">
              <div className="relative group inline-block">
                <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/20 to-[#005a8a]/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
                <button
                  type="button"
                  onClick={onBackToLogin}
                  className={`relative text-sm font-black transition-all duration-300 hover:scale-105 p-3 rounded-lg backdrop-blur-xl ${
                    isDark 
                      ? 'text-[#006da6] hover:text-[#0080c7] hover:bg-white/10 border border-white/20' 
                      : 'text-[#006da6] hover:text-[#0080c7] hover:bg-[#006da6]/10 border border-gray-200'
                  }`}
                  disabled={loading}
                >
                  Back to Sign In
                </button>
              </div>
            </div>
          )}
        </div>
      </form>

      <div className={`text-center p-4 rounded-xl backdrop-blur-xl ${
        isDark ? 'bg-white/5 border border-white/20' : 'bg-white/50 border border-white/40'
      }`}>
        <p className={`text-sm font-medium ${isDark ? 'text-[#CCCCCC]/80' : 'text-[#6B7280]/80'}`}>
          Didn't receive the email? Check your spam folder or try resending.
        </p>
      </div>
    </div>
  );
};

export default EmailVerificationForm;

