import { useState } from 'react';
import { usePasswordReset } from '../../../hooks/useAuth';
import { useTheme } from '../../../contexts/ThemeContext';
import { validatePassword } from '../../../utils/auth';
import LoadingSpinner from '../../common/LoadingSpinner';

const PasswordResetConfirmForm = ({ 
  token,
  onSuccess, 
  onError,
  onBackToLogin,
  className = '' 
}) => {
  const [formData, setFormData] = useState({
    password: '',
    confirm_password: ''
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [focusedFields, setFocusedFields] = useState({});

  const { confirmReset, loading, error, setError } = usePasswordReset();
  const { isDark } = useTheme();

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: '' }));
    }
    if (error) {
      setError(null);
    }
  };

  const handleFocus = (fieldName) => {
    setFocusedFields(prev => ({ ...prev, [fieldName]: true }));
  };

  const handleBlur = (fieldName) => {
    if (!formData[fieldName]) {
      setFocusedFields(prev => ({ ...prev, [fieldName]: false }));
    }
  };

  const validateForm = () => {
    const newErrors = {};

    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else {
      const passwordValidation = validatePassword(formData.password);
      if (!passwordValidation.isValid) {
        const errorMessages = [];
        if (passwordValidation.errors.minLength) errorMessages.push('at least 8 characters');
        if (passwordValidation.errors.hasUpperCase) errorMessages.push('one uppercase letter');
        if (passwordValidation.errors.hasLowerCase) errorMessages.push('one lowercase letter');
        if (passwordValidation.errors.hasNumbers) errorMessages.push('one number');
        newErrors.password = `Password must contain ${errorMessages.join(', ')}`;
      }
    }

    if (!formData.confirm_password) {
      newErrors.confirm_password = 'Please confirm your password';
    } else if (formData.password !== formData.confirm_password) {
      newErrors.confirm_password = 'Passwords do not match';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    const response = await confirmReset(token, formData.password);

    if (response.success) {
      setIsSuccess(true);
      onSuccess?.(response);
    } else {
      onError?.(response.error || 'Password reset failed');
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
    const isActive = focusedFields[fieldName] || formData[fieldName];
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

  // Success State
  if (isSuccess) {
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
            Password Reset Successful
          </h3>
          <p className={`text-base font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
            Your password has been successfully reset. You can now sign in with your new password.
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
              <span className="relative z-10">Sign In Now</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  // Invalid Token State
  if (!token) {
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
            Invalid Reset Link
          </h3>
          <p className={`text-base font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
            This password reset link is invalid or has expired. Please request a new one.
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
              <span className="relative z-10">Back to Sign In</span>
            </button>
          </div>
        )}
      </div>
    );
  }

  // Main Form State
  return (
    <form onSubmit={handleSubmit} className={`space-y-6 animate-fade-in-up ${className}`}>
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
                  d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-3.586l4.293-4.293a1 1 0 011.414 0L10 14l4-4a6 6 0 016-6z" 
                />
              </svg>
            </div>
          </div>
        </div>

        <div className="space-y-3">
          <h2 className={`text-3xl font-black bg-gradient-to-r from-[#006da6] via-[#0080c7] to-[#005a8a] bg-clip-text text-transparent`}>
            Set New Password
          </h2>
          <p className={`text-base font-medium ${isDark ? 'text-[#CCCCCC]' : 'text-[#6B7280]'}`}>
            Enter your new password below to complete the reset process.
          </p>
        </div>
      </div>

      <div className="space-y-5">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              value={formData.password}
              onChange={handleInputChange}
              onFocus={() => handleFocus('password')}
              onBlur={() => handleBlur('password')}
              className={`${getInputClasses('password', errors.password)} pr-12`}
              disabled={loading}
            />
            <label 
              htmlFor="password" 
              className={getLabelClasses('password', errors.password)}
            >
              New Password
            </label>
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-lg transition-all duration-300 z-10 hover:scale-110 ${
                isDark 
                  ? 'text-[#CCCCCC] hover:text-[#006da6] hover:bg-white/10' 
                  : 'text-[#6B7280] hover:text-[#006da6] hover:bg-[#006da6]/10'
              }`}
              disabled={loading}
            >
              {showPassword ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>
          {errors.password && (
            <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.password}</p>
          )}
        </div>

        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="confirm_password"
              name="confirm_password"
              type={showConfirmPassword ? 'text' : 'password'}
              autoComplete="new-password"
              required
              value={formData.confirm_password}
              onChange={handleInputChange}
              onFocus={() => handleFocus('confirm_password')}
              onBlur={() => handleBlur('confirm_password')}
              className={`${getInputClasses('confirm_password', errors.confirm_password)} pr-12`}
              disabled={loading}
            />
            <label 
              htmlFor="confirm_password" 
              className={getLabelClasses('confirm_password', errors.confirm_password)}
            >
              Confirm New Password
            </label>
            <button
              type="button"
              onClick={() => setShowConfirmPassword(!showConfirmPassword)}
              className={`absolute right-3 top-1/2 transform -translate-y-1/2 p-2 rounded-lg transition-all duration-300 z-10 hover:scale-110 ${
                isDark 
                  ? 'text-[#CCCCCC] hover:text-[#006da6] hover:bg-white/10' 
                  : 'text-[#6B7280] hover:text-[#006da6] hover:bg-[#006da6]/10'
              }`}
              disabled={loading}
            >
              {showConfirmPassword ? (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                </svg>
              ) : (
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              )}
            </button>
          </div>
          {errors.confirm_password && (
            <p className="mt-2 text-sm text-red-500 font-semibold animate-fade-in-up">{errors.confirm_password}</p>
          )}
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

      <div className="space-y-4">
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
                  <span>Resetting Password...</span>
                </div>
              ) : (
                'Reset Password'
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
  );
};

export default PasswordResetConfirmForm;

