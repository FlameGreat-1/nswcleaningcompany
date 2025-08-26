import { useState } from 'react';
import { useLogin } from '../../../hooks/useAuth';
import { useTheme } from '../../../contexts/ThemeContext';
import { validateEmail } from '../../../utils/auth';
import LoadingSpinner from '../../common/LoadingSpinner';
import GoogleAuthButton from './GoogleAuthButton';

const LoginForm = ({ 
  onSuccess, 
  onError, 
  onForgotPassword,
  userType = 'client',
  clientType = 'general',
  className = '' 
}) => {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [errors, setErrors] = useState({});
  const [showPassword, setShowPassword] = useState(false);
  const [focusedFields, setFocusedFields] = useState({});

  const { loginUser, loading, error, setError } = useLogin();
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

    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!validateEmail(formData.email)) {
      newErrors.email = 'Please enter a valid email address';
    }

    if (!formData.password.trim()) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'Password must be at least 6 characters';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) return;

    const response = await loginUser({
      email: formData.email.trim(),
      password: formData.password,
      user_type: userType,
      client_type: clientType
    });

    if (response.success) {
      onSuccess?.(response);
    } else {
      if (response.errors) {
        setErrors(response.errors);
      }
      onError?.(response.error || 'Login failed');
    }
  };
  
  const handleGoogleSuccess = (response) => {
    const formattedResponse = {
      success: true,
      user: response.user || (response.data && response.data.user) || {},
      redirectTo: response.redirectTo || null
    };
    
    if (!formattedResponse.user.user_type && response.user_type) {
      formattedResponse.user.user_type = response.user_type;
    }
    
    onSuccess?.(formattedResponse);
  };
  
  const handleGoogleError = (error) => {
    onError?.(error);
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

  return (
    <form onSubmit={handleSubmit} className={`space-y-6 ${className}`}>
      <div className="space-y-5">
        <div className="relative group">
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="email"
              required
              value={formData.email}
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
          <div className="absolute -inset-1 bg-gradient-to-r from-[#006da6]/20 via-[#0080c7]/20 to-[#005a8a]/20 rounded-xl blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
          <div className="relative">
            <input
              id="password"
              name="password"
              type={showPassword ? 'text' : 'password'}
              autoComplete="current-password"
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
              Password
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
      </div>

      {(error || errors.non_field_errors) && (
        <div className={`relative group p-4 rounded-xl border-2 animate-fade-in-up ${
          isDark 
            ? 'bg-red-500/10 border-red-500/30 backdrop-blur-xl' 
            : 'bg-red-50 border-red-200'
        }`}>
          <div className="absolute -inset-1 bg-gradient-to-r from-red-500/20 to-red-600/20 rounded-xl blur opacity-50"></div>
          <p className="relative text-sm text-red-500 font-semibold">
            {error || errors.non_field_errors}
          </p>
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
                  <span>Signing In...</span>
                </div>
              ) : (
                'Sign In'
              )}
            </div>
          </button>
        </div>

        <div className="relative">
          <div className="absolute inset-0 flex items-center">
            <div className={`w-full border-t-2 ${isDark ? 'border-white/20' : 'border-gray-200'}`} />
          </div>
          <div className="relative flex justify-center text-sm">
            <span className={`px-6 font-semibold backdrop-blur-xl rounded-full ${
              isDark 
                ? 'bg-[#180c2e]/80 text-[#CCCCCC] border border-white/10' 
                : 'bg-white/90 text-[#6B7280] border border-gray-200'
            }`}>
              Or continue with
            </span>
          </div>
        </div>

        <GoogleAuthButton
          mode="login"
          userType={userType}
          clientType={clientType}
          onSuccess={handleGoogleSuccess}
          onError={handleGoogleError}
          disabled={loading}
          size="lg"
        />
      </div>

      {onForgotPassword && (
        <div className="text-center">
          <div className="relative group inline-block">
            <div className="absolute -inset-2 bg-gradient-to-r from-[#006da6]/20 to-[#005a8a]/20 rounded-lg blur opacity-0 group-hover:opacity-100 transition-all duration-300"></div>
            <button
              type="button"
              onClick={onForgotPassword}
              className={`relative text-sm font-black transition-all duration-300 hover:scale-105 p-3 rounded-lg backdrop-blur-xl ${
                isDark 
                  ? 'text-[#006da6] hover:text-[#0080c7] hover:bg-white/10 border border-white/20' 
                  : 'text-[#006da6] hover:text-[#0080c7] hover:bg-[#006da6]/10 border border-gray-200'
              }`}
              disabled={loading}
            >
              Forgot your password?
            </button>
          </div>
        </div>
      )}
    </form>
  );
};

export default LoginForm;
